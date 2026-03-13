from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import cache_get, cache_set
from app.config import settings
from app.db import get_db
from app.schemas import Movie, MovieDetail, TopRatedMovie
from app.services import movie_service

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("", response_model=List[Movie])
async def search_movies(
    title: Optional[str] = Query(None, description="Partial title search (case-insensitive)"),
    genre: Optional[str] = Query(None, description="Filter by genre (e.g. Action)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),
    db: AsyncSession = Depends(get_db),
):
    """Search movies by title and/or genre with pagination."""
    cache_key = f"movies:search:{title}:{genre}:{page}:{page_size}"
    cached = await cache_get(cache_key)
    if cached is not None:
        return cached

    movies = await movie_service.search_movies(db, title=title, genre=genre, page=page, page_size=page_size)
    result = [m.model_dump() for m in movies]
    await cache_set(cache_key, result)
    return result


@router.get("/top-rated", response_model=List[TopRatedMovie])
async def top_rated_movies(
    limit: int = Query(10, ge=1, le=100, description="Number of movies to return"),
    min_ratings: int = Query(50, ge=1, description="Minimum number of ratings required"),
    db: AsyncSession = Depends(get_db),
):
    """Return the top-rated movies with a minimum number of ratings."""
    cache_key = f"movies:top_rated:{limit}:{min_ratings}"
    cached = await cache_get(cache_key)
    if cached is not None:
        return cached

    movies = await movie_service.get_top_rated(db, limit=limit, min_ratings=min_ratings)
    result = [m.model_dump() for m in movies]
    await cache_set(cache_key, result)
    return result


@router.get("/{movie_id}", response_model=MovieDetail)
async def get_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    """Return detailed information and rating statistics for a single movie."""
    cache_key = f"movies:detail:{movie_id}"
    cached = await cache_get(cache_key)
    if cached is not None:
        return cached

    movie = await movie_service.get_movie_detail(db, movie_id=movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")

    result = movie.model_dump()
    await cache_set(cache_key, result)
    return result
