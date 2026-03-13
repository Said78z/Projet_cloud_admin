from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import get_cache
from app.db import get_db
from app.schemas import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """Liveness probe – checks DB and Redis connectivity."""
    # Check database
    db_status = "ok"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    # Check Redis
    cache_status = "ok"
    try:
        client = await get_cache()
        await client.ping()
    except Exception:
        cache_status = "error"

    overall = "ok" if db_status == "ok" and cache_status == "ok" else "degraded"
    return HealthResponse(status=overall, database=db_status, cache=cache_status)
