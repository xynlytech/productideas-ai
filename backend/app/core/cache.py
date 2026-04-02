import hashlib
import json
import logging
from functools import wraps
from typing import Any

import redis.asyncio as redis

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_redis_pool: redis.Redis | None = None

CACHE_TTL_SHORT = 60  # 1 minute
CACHE_TTL_MEDIUM = 300  # 5 minutes
CACHE_TTL_LONG = 900  # 15 minutes


async def get_redis() -> redis.Redis:
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis_pool


def _make_cache_key(prefix: str, params: dict) -> str:
    """Generate a deterministic cache key from prefix and params."""
    sorted_params = json.dumps(params, sort_keys=True, default=str)
    param_hash = hashlib.sha256(sorted_params.encode()).hexdigest()[:16]
    return f"cache:{prefix}:{param_hash}"


async def cache_get(key: str) -> Any | None:
    try:
        r = await get_redis()
        data = await r.get(key)
        if data:
            return json.loads(data)
    except Exception as e:
        logger.warning(f"Cache get error: {e}")
    return None


async def cache_set(key: str, value: Any, ttl: int = CACHE_TTL_MEDIUM) -> None:
    try:
        r = await get_redis()
        await r.setex(key, ttl, json.dumps(value, default=str))
    except Exception as e:
        logger.warning(f"Cache set error: {e}")


async def cache_invalidate(pattern: str) -> None:
    """Invalidate all cache keys matching a pattern."""
    try:
        r = await get_redis()
        keys = []
        async for key in r.scan_iter(match=pattern):
            keys.append(key)
        if keys:
            await r.delete(*keys)
            logger.info(f"Invalidated {len(keys)} cache keys matching '{pattern}'")
    except Exception as e:
        logger.warning(f"Cache invalidate error: {e}")
