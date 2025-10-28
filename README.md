# Distributed Prime Counter

A high-performance distributed system for counting prime numbers using FastAPI, Celery, Redis, and Nuxt 3.

## 📋 Table of Contents

- [Architecture](#architecture)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [API Usage](#api-usage)
- [Development](#development)
- [Testing](#testing)
- [Configuration](#configuration)
- [Resource Considerations](#resource-considerations)
- [Troubleshooting](#troubleshooting)

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Nuxt 3    │────▶│   FastAPI    │────▶│    Redis    │
│  Frontend   │     │   Backend    │     │   Broker    │
└─────────────┘     └──────────────┘     └─────────────┘
                            │                    │
                            │                    │
                            ▼                    ▼
                    ┌──────────────┐     ┌─────────────┐
                    │    Celery    │────▶│    Redis    │
                    │   Workers    │     │   Backend   │
                    └──────────────┘     └─────────────┘
```

**Components:**

- **Frontend**: Nuxt 3 with TypeScript and TailwindCSS - Beautiful, responsive UI with real-time polling
- **API**: FastAPI with Pydantic validation and automatic OpenAPI documentation
- **Task Queue**: Celery 5.x with chord pattern for distributed task coordination
- **Broker/Backend**: Redis 7 for message queuing and result storage
- **Containerization**: Docker and Docker Compose for easy deployment

## Features

- 🚀 **Parallel Processing**: Divide work into configurable chunks processed simultaneously
- 📊 **Real-time Progress**: Live progress tracking via Redis with sub-second updates
- 🔄 **State Management**: Complete job lifecycle (PENDING → STARTED → PROGRESS → SUCCESS/FAILURE)
- 📈 **Scalable Workers**: Horizontally scale workers with a single command
- 📚 **OpenAPI Docs**: Interactive API documentation at `/docs`
- ✅ **Input Validation**: Robust validation with clear error messages
- 🎨 **Modern UI**: Beautiful gradient design with progress animations
- 🔒 **Type Safety**: Full TypeScript frontend and typed Python backend

## Prerequisites

- **Docker** and **Docker Compose** (required)
- **Node.js 18+** and **Python 3.11+** (optional, for local development)

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd <directory>

# Copy environment variables
cp .env.example .env
```

### 2. Start All Services

```bash
# Start with default configuration (1 worker)
docker compose up --build

# Or start with multiple workers for better performance
docker compose up --build --scale worker=3
```

### 3. Access the Application

- **Web Interface**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **API Base URL**: http://localhost:8000
- **Health Check**: http://localhost:8000/health

### 4. Run Verification Tests

```bash
# Wait for all services to start, then run:
./test_verification.sh
```

## API Usage

### Submit a Prime Counting Job

```bash
curl -X POST http://localhost:8000/api/count-primes \
  -H "Content-Type: application/json" \
  -d '{"n":200000,"chunks":16}'
```

**Response (202 Accepted):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "PENDING"
}
```

### Check Job Status

```bash
curl http://localhost:8000/api/jobs/550e8400-e29b-41d4-a716-446655440000
```

**Response (In Progress):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "state": "PROGRESS",
  "progress": {
    "completed": 8,
    "total": 16
  }
}
```

**Response (Completed):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "state": "SUCCESS",
  "result": {
    "prime_count": 17984,
    "duration_sec": 2.45
  }
}
```

### Other Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Root endpoint info
curl http://localhost:8000/

# OpenAPI JSON schema
curl http://localhost:8000/openapi.json
```

## Development

### Backend Development (FastAPI + Celery)

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start Redis (if not using Docker)
redis-server

# Start FastAPI server
uvicorn app.main:app --reload --port 8000

# Start Celery worker (in another terminal)
celery -A app.celery_app worker --loglevel=info
```

### Frontend Development (Nuxt 3)

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
npm start
```

### Project Structure

```
datafuse/
├── docker-compose.yml          # Container orchestration
├── .env.example               # Environment variables template
├── README.md                  # This file
├── backend/
│   ├── Dockerfile            # Backend container image
│   ├── requirements.txt      # Python dependencies
│   ├── pytest.ini           # Test configuration
│   └── app/
│       ├── main.py          # FastAPI application
│       ├── api.py           # API endpoints
│       ├── schemas.py       # Pydantic models
│       ├── celery_app.py    # Celery configuration
│       ├── tasks.py         # Celery task definitions
│       ├── utils.py         # Prime counting logic
│       └── tests/
│           ├── test_prime.py        # Unit tests
└── frontend/
    ├── Dockerfile           # Frontend container image
    ├── package.json         # Node dependencies
    ├── tsconfig.json        # TypeScript config
    ├── nuxt.config.ts       # Nuxt 3 config
    ├── pages/
    │   └── index.vue       # Main page
    ├── components/        # Vue components
    └── app.vue           # App wrapper
```

## Testing

### Run Unit Tests

```bash
cd backend
pytest app/tests/test_prime.py -v
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REDIS_URL` | Redis connection URL | `redis://redis:6379/0` |
| `CELERY_BROKER_URL` | Celery broker URL | `redis://redis:6379/0` |
| `CELERY_RESULT_BACKEND` | Celery result backend | `redis://redis:6379/0` |
| `API_HOST` | API host address | `0.0.0.0` |
| `API_PORT` | API port | `8000` |
| `NEXT_PUBLIC_API_BASE_URL` | Frontend API base URL | `http://localhost:8000` |
| `CELERY_WORKER_CONCURRENCY` | Workers per container | `2` |

### Input Validation Rules

| Parameter | Type | Constraint | Description |
|-----------|------|------------|-------------|
| `n` | integer | `>= 10,000` | Upper limit for prime search |
| `chunks` | integer | `1-128` | Number of parallel processing chunks |

**Why these limits?**
- `n >= 10,000`: Ensures meaningful workload for distributed processing
- `chunks: 1-128`: Balance between parallelism and overhead

### Progress Calculation

The system uses a **contiguous range splitting algorithm**:

1. **Range Division**: The range `1..n` is divided into `chunks` contiguous segments
   - Example: `n=100, chunks=4` → `[1-25, 26-50, 51-75, 76-100]`
   - Each chunk gets roughly equal size: `chunk_size = n ÷ chunks`
   - Last chunk absorbs any remainder

2. **Progress Tracking**: 
   - Each worker increments a Redis counter upon completion
   - Progress = `completed_chunks / total_chunks`
   - Frontend polls every 1 second for updates

3. **Result Aggregation**:
   - Uses Celery **chord pattern**: `group(subtasks) | callback`
   - All subtasks run in parallel
   - Callback aggregates results when all complete
   - Total duration = end-to-end time (includes coordination overhead)

4. **Edge Cases**:
   - If any subtask fails, entire job fails
   - Progress counters are cleaned up on completion or failure
   - Progress keys expire after 1 hour in Redis

### Performance Tips

1. **Worker Scaling**: Scale workers to match available CPU cores
   ```bash
   docker compose up --scale worker=4
   ```

2. **Chunk Sizing**: More chunks = better parallelism but more overhead
   - Small `n` (< 100K): Use 4-8 chunks
   - Medium `n` (100K-500K): Use 16-32 chunks  
   - Large `n` (> 500K): Use 32-64 chunks

### Example Benchmarks

| n | chunks | workers | duration | primes found |
|---|--------|---------|----------|--------------|
| 10,000 | 4 | 1 | ~0.5s | 1,229 |
| 50,000 | 8 | 2 | ~1.2s | 5,133 |
| 100,000 | 16 | 2 | ~2.8s | 9,592 |
| 200,000 | 16 | 3 | ~5.2s | 17,984 |
| 500,000 | 32 | 4 | ~18s | 41,538 |
| 1,000,000 | 32 | 4 | ~45s | 78,498 |

*Note: Actual performance depends on hardware*

## Troubleshooting

### Workers Not Starting

**Symptoms**: Jobs stuck in PENDING state

**Solutions**:
```bash
# Check worker logs
docker compose logs worker

# Verify Redis is running
docker compose ps redis
redis-cli ping

# Restart workers
docker compose restart worker

# Check worker registration
docker compose exec api python -c "from app.celery_app import celery_app; print(celery_app.control.inspect().active())"
```

### Frontend Can't Connect to API

**Symptoms**: CORS errors or connection refused

**Solutions**:
1. Verify `NEXT_PUBLIC_API_BASE_URL` in frontend `.env`
2. Check CORS configuration in `backend/app/main.py`
3. Ensure API container is running: `docker compose ps api`
4. Test API directly: `curl http://localhost:8000/health`

### Redis Connection Errors

**Symptoms**: "Error 111 connecting to redis", "Connection refused"

**Solutions**:
```bash
# Check Redis logs
docker compose logs redis

# Verify Redis is healthy
docker compose exec redis redis-cli ping

# Check network connectivity
docker compose exec api ping redis

# Restart Redis
docker compose restart redis
```

### Jobs Taking Too Long

**Solutions**:
1. Scale workers: `docker compose up --scale worker=5`
2. Reduce chunk size for better parallelism
3. Check system resources: `docker stats`
4. Monitor Redis memory: `redis-cli info memory`

### Memory Issues

**Symptoms**: OOM errors, slow performance

**Solutions**:
```bash
# Check resource usage
docker stats

# Increase Docker memory limit (Docker Desktop)
# Settings → Resources → Memory → 4GB+

# Configure Redis maxmemory
docker compose exec redis redis-cli CONFIG SET maxmemory 1gb
docker compose exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f worker
docker compose logs -f api
docker compose logs -f redis

# Last 100 lines
docker compose logs --tail=100 worker
```

## Acceptance Checklist

Verify the system works correctly:

- [ ] Submitting the form returns 202 with a `job_id`
- [ ] Workers can be scaled: `docker compose up --scale worker=3`
- [ ] Multiple workers process different chunks in parallel
- [ ] Job status transitions: PENDING → STARTED → PROGRESS → SUCCESS
- [ ] Progress numbers reflect `completed/total` chunks correctly
- [ ] Final result is consistent across repeated runs with same `n`
- [ ] OpenAPI documentation available at http://localhost:8000/docs
- [ ] CORS allows requests from http://localhost:3000
- [ ] Input validation rejects `n < 10000` with 400 error
- [ ] Input validation rejects `chunks < 1` or `chunks > 128`
- [ ] Progress bar updates in real-time on frontend
- [ ] Error states are displayed clearly
- [ ] Health check endpoint returns worker count

## Acknowledgments

Built with:

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Celery](https://docs.celeryq.dev/) - Distributed task queue
- [Redis](https://redis.io/) - In-memory data store
- [Nuxt 3](https://nuxt.com/) - Vue.js framework
- [Docker](https://www.docker.com/) - Containerization platform
- [Cursor](https://cursor.com/home) - AI Code Editor

---

**Disclaimer** - Parts of this application like the celery/redis implementation in the backend were implemented with the help of AI agents and Cursor, the AI code editor.
