import json
from typing import Optional

import redis.asyncio as aioredis

from app.config import settings

_redis_client: Optional[aioredis.Redis] = None


async def get_cache() -> aioredis.Redis:
    """Return (and lazily create) the shared Redis client."""
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


async def cache_get(key: str):
    """Return the cached value for *key*, or ``None`` if not found."""
    client = await get_cache()
    value = await client.get(key)
    if value is None:
        return None
    return json.loads(value)


async def cache_set(key: str, value, ttl: int = None):
    """Store *value* (JSON-serialisable) under *key* with an optional TTL."""
    if ttl is None:
        ttl = settings.CACHE_TTL
    client = await get_cache()
    await client.set(key, json.dumps(value), ex=ttl)
