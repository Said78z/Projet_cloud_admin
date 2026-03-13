# MovieLens Service

A REST API for querying and analysing the [MovieLens](https://grouplens.org/datasets/movielens/) dataset under load.

## Features

| Feature | Endpoint |
|---------|----------|
| Search movies by title | `GET /movies?title=<query>` |
| Filter movies by genre | `GET /movies?genre=<genre>` |
| Movie detail + rating stats | `GET /movies/{movie_id}` |
| Top-rated movies | `GET /movies/top-rated` |
| Per-genre statistics | `GET /stats/genres` |
| Rating distribution | `GET /stats/ratings/distribution` |
| Health / liveness probe | `GET /health` |

## Stack

| Component | Technology |
|-----------|-----------|
| API | FastAPI + Uvicorn |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Containerisation | Docker / Docker Compose |
| Load testing | k6 |

## Quick start

```bash
# 1. Clone the repo and enter the service directory
cd movielens-service

# 2. Copy the example environment file
cp .env.example .env

# 3. Start all services
docker compose up --build
```

The API will be available at <http://localhost:8000>.  
Interactive docs are at <http://localhost:8000/docs>.

## Importing data

Download the [MovieLens dataset](https://grouplens.org/datasets/movielens/latest/) and unzip it:

```bash
# Install script dependencies
pip install psycopg2-binary python-dotenv

# Run the importer (adjust --data-dir to match your download)
python scripts/import_data.py --data-dir /path/to/ml-latest-small
```

## Running load tests

```bash
# Install k6: https://k6.io/docs/get-started/installation/
k6 run load-tests/baseline.js

# Override the target URL
k6 run -e BASE_URL=http://localhost:8000 load-tests/baseline.js
```

## Project layout

```
movielens-service/
├── app/
│   ├── main.py              # FastAPI application factory
│   ├── config.py            # Pydantic settings (reads .env)
│   ├── db.py                # Async SQLAlchemy engine & session
│   ├── cache.py             # Redis async client helpers
│   ├── schemas.py           # Pydantic request/response models
│   ├── routers/
│   │   ├── health.py        # GET /health
│   │   ├── movies.py        # GET /movies, /movies/{id}, /movies/top-rated
│   │   └── stats.py         # GET /stats/genres, /stats/ratings/distribution
│   └── services/
│       ├── movie_service.py # Movie query logic
│       └── stats_service.py # Stats query logic
├── sql/
│   ├── schema.sql           # Table definitions
│   ├── indexes.sql          # Performance indexes
│   └── sample_queries.sql   # Handy ad-hoc queries
├── scripts/
│   └── import_data.py       # MovieLens CSV → PostgreSQL importer
├── load-tests/
│   └── baseline.js          # k6 baseline scenario
├── .env.example
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@db:5432/movielens` | Async SQLAlchemy DSN |
| `REDIS_URL` | `redis://redis:6379` | Redis connection URL |
| `CACHE_TTL` | `300` | Cache entry lifetime in seconds |
