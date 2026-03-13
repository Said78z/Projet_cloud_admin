from typing import Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import cache_get, cache_set
from app.db import get_db
from app.schemas import GenreStats
from app.services import stats_service

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/genres", response_model=List[GenreStats])
async def genre_stats(db: AsyncSession = Depends(get_db)):
    """Return movie counts and average ratings grouped by genre."""
    cache_key = "stats:genres"
    cached = await cache_get(cache_key)
    if cached is not None:
        return cached

    stats = await stats_service.get_genre_stats(db)
    result = [s.model_dump() for s in stats]
    await cache_set(cache_key, result)
    return result


@router.get("/ratings/distribution", response_model=Dict[str, int])
async def rating_distribution(db: AsyncSession = Depends(get_db)):
    """Return the global distribution of rating values."""
    cache_key = "stats:rating_distribution"
    cached = await cache_get(cache_key)
    if cached is not None:
        return cached

    distribution = await stats_service.get_rating_distribution(db)
    await cache_set(cache_key, distribution)
    return distribution
