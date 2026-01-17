"""Redis Cache Configuration

Redis caching for sessions, AHCIP codes, and rule definitions.
"""

import json
from typing import Optional, Any
import redis.asyncio as redis
from functools import wraps

from app.core.config import settings


class RedisCache:
    """Redis cache client wrapper."""
    
    def __init__(self):
        self._client: Optional[redis.Redis] = None
    
    async def get_client(self) -> redis.Redis:
        """Get or create Redis client."""
        if self._client is None:
            self._client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
        return self._client
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        client = await self.get_client()
        return await client.get(key)
    
    async def set(
        self,
        key: str,
        value: str,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional TTL."""
        client = await self.get_client()
        if ttl:
            return await client.setex(key, ttl, value)
        return await client.set(key, value)
    
    async def delete(self, key: str) -> int:
        """Delete key from cache."""
        client = await self.get_client()
        return await client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        client = await self.get_client()
        return await client.exists(key) > 0
    
    async def get_json(self, key: str) -> Optional[Any]:
        """Get JSON value from cache."""
        value = await self.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set_json(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set JSON value in cache."""
        return await self.set(key, json.dumps(value), ttl)
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter."""
        client = await self.get_client()
        return await client.incrby(key, amount)
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration on key."""
        client = await self.get_client()
        return await client.expire(key, ttl)
    
    async def close(self):
        """Close Redis connection."""
        if self._client:
            await self._client.close()


# Global cache instance
cache = RedisCache()


# Cache key prefixes
class CacheKeys:
    """Cache key prefixes for different data types."""
    SESSION = "session:"
    AHCIP_CODE = "ahcip:"
    AHCIP_CODES = "ahcip_codes"  # For bulk AHCIP code cache
    RULE = "rule:"
    ACTIVE_RULES = "active_rules"  # For active rules cache
    TEMPLATE = "template:"
    RATE_LIMIT = "ratelimit:"
    USER = "user:"


def cached(key_prefix: str, ttl: int):
    """Decorator for caching function results."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function arguments
            cache_key = f"{key_prefix}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_value = await cache.get_json(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache.set_json(cache_key, result, ttl)
            return result
        return wrapper
    return decorator
