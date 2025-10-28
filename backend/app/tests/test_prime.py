"""Tests for prime counting utilities."""
import pytest
from app.utils import is_prime, count_primes_in_range, split_range


class TestIsPrime:
    
    def test_small_primes(self):
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        for p in primes:
            assert is_prime(p), f"{p} should be prime"
    
    def test_small_non_primes(self):
        non_primes = [0, 1, 4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20]
        for n in non_primes:
            assert not is_prime(n), f"{n} should not be prime"
    
    def test_negative_numbers(self):
        assert not is_prime(-5)
        assert not is_prime(-1)
    
    def test_large_prime(self):
        assert is_prime(104729)  # A known prime
    
    def test_large_non_prime(self):
        assert not is_prime(104730)  # 104729 + 1


class TestCountPrimesInRange:
    
    def test_range_1_to_10(self):
        assert count_primes_in_range(1, 10) == 4
    
    def test_range_1_to_100(self):
        assert count_primes_in_range(1, 100) == 25
    
    def test_range_with_no_primes(self):
        assert count_primes_in_range(24, 28) == 0
    
    def test_single_prime(self):
        assert count_primes_in_range(7, 7) == 1
    
    def test_single_non_prime(self):
        assert count_primes_in_range(8, 8) == 0
    
    def test_range_2_to_10(self):
        assert count_primes_in_range(2, 10) == 4


class TestSplitRange:
    
    def test_even_split(self):
        ranges = split_range(100, 4)
        assert len(ranges) == 4
        assert ranges == [(1, 25), (26, 50), (51, 75), (76, 100)]
    
    def test_uneven_split(self):
        ranges = split_range(100, 3)
        assert len(ranges) == 3
        assert ranges[0] == (1, 33)
        assert ranges[1] == (34, 66)
        assert ranges[2] == (67, 100)
    
    def test_single_chunk(self):
        ranges = split_range(100, 1)
        assert len(ranges) == 1
        assert ranges[0] == (1, 100)
    
    def test_more_chunks_than_range(self):
        ranges = split_range(10, 5)
        assert len(ranges) == 5
        assert ranges[0] == (1, 2)
        assert ranges[1] == (3, 4)
        assert ranges[2] == (5, 6)
        assert ranges[3] == (7, 8)
        assert ranges[4] == (9, 10)
    
    def test_large_n(self):
        ranges = split_range(200000, 16)
        assert len(ranges) == 16
        assert ranges[0][0] == 1
        assert ranges[-1][1] == 200000
        for i in range(len(ranges) - 1):
            assert ranges[i][1] + 1 == ranges[i + 1][0]


class TestIntegration:
    
    def test_split_and_count(self):
        n = 100
        chunks = 4
        ranges = split_range(n, chunks)
        
        counts = [count_primes_in_range(start, end) for start, end in ranges]
        total = sum(counts)
        
        # Should equal the total count from 1 to 100
        assert total == count_primes_in_range(1, 100)
        assert total == 25
    
    def test_split_and_count_large(self):
        n = 1000
        chunks = 8
        ranges = split_range(n, chunks)
        
        counts = [count_primes_in_range(start, end) for start, end in ranges]
        total = sum(counts)
        
        # Should equal the total count from 1 to 1000
        assert total == count_primes_in_range(1, 1000)


