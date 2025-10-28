"""Main FastAPI application."""
import logging
import time
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.schemas import (
    CountPrimesRequest,
    CountPrimesResponse,
    JobStatusResponse,
    ProgressInfo,
    JobResult,
)
from app.tasks import count_primes_task
from app.celery_app import celery_app
import redis
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting API server")
    yield
    logger.info("Shutting down API server")


app = FastAPI(
    title="Prime Counter API",
    description="Prime counting service using Celery and Redis",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    start_time = time.time()
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    logger.info(
        f"Request completed: {request.method} {request.url.path} "
        f"- Status: {response.status_code} - Duration: {duration:.3f}s"
    )
    
    return response


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Prime Counter API",
        "docs": "/docs",
        "endpoints": {
            "submit_job": "POST /api/count-primes",
            "check_status": "GET /api/jobs/{job_id}"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        redis_client.ping()
        redis_status = "healthy"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        redis_status = "unhealthy"
    
    inspector = celery_app.control.inspect()
    active_workers = inspector.active()
    worker_count = len(active_workers) if active_workers else 0
    
    return {
        "status": "healthy" if redis_status == "healthy" else "degraded",
        "redis": redis_status,
        "workers": worker_count
    }


@app.post("/api/count-primes", response_model=CountPrimesResponse, status_code=202)
async def count_primes(request: CountPrimesRequest):
    """
    Submit a job to count prime numbers up to n.
    
    The range 1..n is split into the specified number of chunks,
    and each chunk is processed in parallel by Celery workers.
    
    Args:
        request: Request containing n (upper limit) and chunks (parallelism)
        
    Returns:
        Job ID and initial status
        
    Raises:
        HTTPException: If validation fails (400)
    """
    logger.info(f"Received count-primes request: n={request.n}, chunks={request.chunks}")
    
    try:
        result = count_primes_task.apply_async(
            args=[request.n, request.chunks],
            task_id=None,
        )
        
        job_id = result.id
        logger.info(f"Created job {job_id} for n={request.n}, chunks={request.chunks}")
        
        return CountPrimesResponse(
            job_id=job_id,
            status="PENDING"
        )
        
    except Exception as e:
        logger.error(f"Failed to create job: {e}")
        raise HTTPException(status_code=500, detail="Failed to create job")


@app.get("/api/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get the status of a job.
    
    Args:
        job_id: Unique job identifier
        
    Returns:
        Job status including state, progress, and result
        
    Raises:
        HTTPException: If job not found (404)
    """
    logger.info(f"Checking status for job {job_id}")
    
    try:
        result = celery_app.AsyncResult(job_id)
        
        progress_key = f"job:{job_id}:progress"
        progress_data = redis_client.get(progress_key)
        
        progress = None
        if progress_data:
            completed, total = map(int, progress_data.decode().split(':'))
            progress = ProgressInfo(completed=completed, total=total)
        
        state = result.state
        
        if state == 'PENDING':
            return JobStatusResponse(
                job_id=job_id,
                state="PENDING",
                progress=None
            )
        
        elif state == 'STARTED':
            return JobStatusResponse(
                job_id=job_id,
                state="STARTED",
                progress=progress
            )
        
        elif state == 'PROGRESS':
            return JobStatusResponse(
                job_id=job_id,
                state="PROGRESS",
                progress=progress
            )
        
        elif state == 'SUCCESS':
            result_data = result.result
            
            if isinstance(result_data, str):
                chord_result = celery_app.AsyncResult(result_data)
                if chord_result.state == 'SUCCESS':
                    chord_data = chord_result.result
                    job_result = JobResult(
                        prime_count=chord_data['prime_count'],
                        duration_sec=chord_data['duration_sec']
                    )
                    return JobStatusResponse(
                        job_id=job_id,
                        state="SUCCESS",
                        progress=progress,
                        result=job_result
                    )
                elif chord_result.state == 'FAILURE':
                    error_msg = str(chord_result.info) if chord_result.info else "Chord failed"
                    logger.error(f"Chord for job {job_id} failed: {error_msg}")
                    return JobStatusResponse(
                        job_id=job_id,
                        state="FAILURE",
                        error=error_msg
                    )
                else:
                    # Chord still processing, show progress
                    return JobStatusResponse(
                        job_id=job_id,
                        state="PROGRESS",
                        progress=progress
                    )
            else:
                job_result = JobResult(
                    prime_count=result_data['prime_count'],
                    duration_sec=result_data['duration_sec']
                )
                return JobStatusResponse(
                    job_id=job_id,
                    state="SUCCESS",
                    progress=progress,
                    result=job_result
                )
        
        elif state == 'FAILURE':
            error_msg = str(result.info) if result.info else "Unknown error"
            logger.error(f"Job {job_id} failed: {error_msg}")
            return JobStatusResponse(
                job_id=job_id,
                state="FAILURE",
                error=error_msg
            )
        
        else:
            logger.warning(f"Unknown state {state} for job {job_id}")
            return JobStatusResponse(
                job_id=job_id,
                state="PENDING"
            )
            
    except Exception as e:
        logger.error(f"Error checking job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error checking job status: {str(e)}")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler."""
    logger.error(f"HTTP error {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

