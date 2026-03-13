from fastapi import FastAPI

from app.routers import health, movies, stats

app = FastAPI(
    title="MovieLens Service",
    description="REST API for querying and analysing the MovieLens dataset.",
    version="1.0.0",
)

app.include_router(health.router)
app.include_router(movies.router)
app.include_router(stats.router)
