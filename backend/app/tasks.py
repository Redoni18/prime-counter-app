"""Celery tasks for distributed prime counting."""
import logging
import time
import redis
import os
from typing import Dict, Any
from celery import chord, group
from app.celery_app import celery_app
from app.utils import count_primes_in_range, split_range

logger = logging.getLogger(__name__)

redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
redis_client = redis.from_url(redis_url)


@celery_app.task(bind=True, name='app.tasks.count_primes_chunk')
def count_primes_chunk(self, start: int, end: int, job_id: str, chunk_idx: int) -> Dict[str, Any]:
    """
    Count primes in a specific range chunk.
    
    This task is executed by workers in parallel for each chunk of the range.
    
    Args:
        start: Start of range (inclusive)
        end: End of range (inclusive)
        job_id: Parent job ID for progress tracking
        chunk_idx: Index of this chunk
        
    Returns:
        Dictionary with prime_count and duration for this chunk
    """
    task_start = time.time()
    
    logger.info(f"[Job {job_id}] Chunk {chunk_idx}: Counting primes in range [{start}, {end}]")
    
    try:
        prime_count = count_primes_in_range(start, end)
        
        duration = time.time() - task_start
        
        progress_key = f"job:{job_id}:progress"
        completed_key = f"job:{job_id}:completed"
        
        completed = redis_client.incr(completed_key)
        
        total_key = f"job:{job_id}:total"
        total = int(redis_client.get(total_key) or 0)
        
        redis_client.set(progress_key, f"{completed}:{total}", ex=3600)
        
        if completed < total:
            self.update_state(
                state='PROGRESS',
                meta={'completed': completed, 'total': total}
            )
        
        logger.info(
            f"[Job {job_id}] Chunk {chunk_idx}: Found {prime_count} primes "
            f"in {duration:.3f}s (Progress: {completed}/{total})"
        )
        
        return {
            'prime_count': prime_count,
            'duration': duration,
            'chunk_idx': chunk_idx,
            'range': [start, end]
        }
        
    except Exception as e:
        logger.error(f"[Job {job_id}] Chunk {chunk_idx} failed: {e}")
        redis_client.delete(f"job:{job_id}:completed")
        redis_client.delete(f"job:{job_id}:total")
        redis_client.delete(f"job:{job_id}:progress")
        raise


@celery_app.task(bind=True, name='app.tasks.aggregate_results')
def aggregate_results(self, results: list, job_id: str, start_time: float) -> Dict[str, Any]:
    """
    Aggregate results from all chunk tasks.
    
    This is the callback task that runs after all chunks complete.
    
    Args:
        results: List of results from all chunk tasks
        job_id: Job ID
        start_time: Start time of the overall job
        
    Returns:
        Final aggregated result with total prime count and duration
    """
    logger.info(f"[Job {job_id}] Aggregating results from {len(results)} chunks")
    
    try:
        total_primes = sum(r['prime_count'] for r in results)
        
        total_duration = time.time() - start_time
        
        redis_client.delete(f"job:{job_id}:completed")
        redis_client.delete(f"job:{job_id}:total")
        redis_client.expire(f"job:{job_id}:progress", 300)
        
        result = {
            'prime_count': total_primes,
            'duration_sec': round(total_duration, 3),
            'chunks_processed': len(results)
        }
        
        logger.info(
            f"[Job {job_id}] Complete: {total_primes} primes found "
            f"in {total_duration:.3f}s across {len(results)} chunks"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"[Job {job_id}] Aggregation failed: {e}")
        # Clean up on error
        redis_client.delete(f"job:{job_id}:completed")
        redis_client.delete(f"job:{job_id}:total")
        redis_client.delete(f"job:{job_id}:progress")
        raise


@celery_app.task(bind=True, name='app.tasks.count_primes_task')
def count_primes_task(self, n: int, chunks: int) -> str:
    """
    Main task to count primes from 1 to n using parallel chunks.
    
    This task orchestrates the work by:
    1. Splitting the range into chunks
    2. Creating subtasks for each chunk
    3. Launching them with a chord pattern
    
    Args:
        n: Upper limit for prime search
        chunks: Number of parallel chunks
        
    Returns:
        Chord result ID (the chord callback will have the final result)
    """
    job_id = self.request.id
    start_time = time.time()
    
    logger.info(f"[Job {job_id}] Starting prime count for n={n}, chunks={chunks}")
    
    self.update_state(state='STARTED', meta={'n': n, 'chunks': chunks})
    
    try:
        ranges = split_range(n, chunks)
        
        redis_client.set(f"job:{job_id}:completed", 0, ex=3600)
        redis_client.set(f"job:{job_id}:total", chunks, ex=3600)
        redis_client.set(f"job:{job_id}:progress", f"0:{chunks}", ex=3600)
        
        logger.info(f"[Job {job_id}] Split range into {len(ranges)} chunks: {ranges}")
        
        # Create a chord: group of chunk tasks + aggregation callback
        chord_result = chord(
            group(
                count_primes_chunk.s(start, end, job_id, idx)
                for idx, (start, end) in enumerate(ranges)
            )
        )(aggregate_results.s(job_id, start_time))
        
        return chord_result.id
        
    except Exception as e:
        logger.error(f"[Job {job_id}] Failed: {e}")
        redis_client.delete(f"job:{job_id}:completed")
        redis_client.delete(f"job:{job_id}:total")
        redis_client.delete(f"job:{job_id}:progress")
        raise

