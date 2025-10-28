"""Utility functions for prime counting."""
import math
from typing import Tuple


def is_prime(n: int) -> bool:
    """
    Check if a number is prime.
    
    Args:
        n: Number to check
        
    Returns:
        True if n is prime, False otherwise
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def count_primes_in_range(start: int, end: int) -> int:
    """
    Count prime numbers in a given range [start, end].
    
    Args:
        start: Start of range (inclusive)
        end: End of range (inclusive)
        
    Returns:
        Number of primes in the range
    """
    count = 0
    for num in range(start, end + 1):
        if is_prime(num):
            count += 1
    return count


def split_range(n: int, chunks: int) -> list[Tuple[int, int]]:
    """
    Split range 1..n into approximately equal chunks.
    
    Args:
        n: Upper limit of range
        chunks: Number of chunks to create
        
    Returns:
        List of (start, end) tuples representing each chunk
    """
    chunk_size = n // chunks
    ranges = []
    
    for i in range(chunks):
        start = i * chunk_size + 1
        end = n if i == chunks - 1 else (i + 1) * chunk_size
        ranges.append((start, end))
    
    return ranges


