"""Request and response schemas for the API."""
from typing import Optional, Literal
from pydantic import BaseModel, Field, validator


class CountPrimesRequest(BaseModel):
    n: int = Field(..., description="Upper limit for prime search", ge=10_000)
    chunks: int = Field(..., description="Number of parallel chunks", ge=1, le=128)

    @validator('n')
    def validate_n(cls, v):
        if v < 10_000:
            raise ValueError('n must be >= 10000')
        return v

    @validator('chunks')
    def validate_chunks(cls, v):
        if v < 1 or v > 128:
            raise ValueError('chunks must be between 1 and 128')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "n": 200000,
                "chunks": 16
            }
        }


class CountPrimesResponse(BaseModel):
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Initial job status")

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "PENDING"
            }
        }


class ProgressInfo(BaseModel):
    completed: int = Field(..., description="Number of completed chunks")
    total: int = Field(..., description="Total number of chunks")


class JobResult(BaseModel):
    prime_count: int = Field(..., description="Total number of primes found")
    duration_sec: float = Field(..., description="Total execution time in seconds")


class JobStatusResponse(BaseModel):
    job_id: str = Field(..., description="Unique job identifier")
    state: Literal["PENDING", "STARTED", "PROGRESS", "SUCCESS", "FAILURE"] = Field(
        ..., description="Current job state"
    )
    progress: Optional[ProgressInfo] = Field(None, description="Progress information")
    result: Optional[JobResult] = Field(None, description="Final result if completed")
    error: Optional[str] = Field(None, description="Error message if failed")

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "state": "PROGRESS",
                "progress": {
                    "completed": 8,
                    "total": 16
                }
            }
        }


