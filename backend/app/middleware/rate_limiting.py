"""Rate Limiting Middleware

Token bucket rate limiting per provider/user.
"""

import time
from typing import Callable, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

from app.core.config import settings
from app.core.cache import cache, CacheKeys


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Middleware for API rate limiting."""
    
    def __init__(self, app, rate_limit: int = None, burst_limit: int = None):
        super().__init__(app)
        self.rate_limit = rate_limit or settings.RATE_LIMIT_PER_MINUTE
        self.burst_limit = burst_limit or settings.RATE_LIMIT_BURST
        self.window_size = 60  # 1 minute window
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check rate limit before processing request."""
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/"]:
            return await call_next(request)
        
        # Get identifier for rate limiting
        identifier = await self._get_identifier(request)
        
        # Check rate limit
        is_allowed, remaining, reset_time = await self._check_rate_limit(identifier)
        
        if not is_allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                    "retry_after": reset_time,
                },
                headers={
                    "X-RateLimit-Limit": str(self.rate_limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_time),
                    "Retry-After": str(reset_time),
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)
        
        return response
    
    async def _get_identifier(self, request: Request) -> str:
        """Get identifier for rate limiting (user ID, API key, or IP)."""
        # Check for authenticated user
        if hasattr(request.state, "user_id"):
            return f"user:{request.state.user_id}"
        
        # Check for API key
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api:{api_key[:16]}"
        
        # Fall back to IP address
        client_ip = self._get_client_ip(request)
        return f"ip:{client_ip}"
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        if request.client:
            return request.client.host
        
        return "unknown"
    
    async def _check_rate_limit(
        self,
        identifier: str
    ) -> tuple[bool, int, int]:
        """Check if request is within rate limit.
        
        Returns:
            Tuple of (is_allowed, remaining_requests, reset_time)
        """
        cache_key = f"{CacheKeys.RATE_LIMIT}{identifier}"
        current_time = int(time.time())
        window_start = current_time - self.window_size
        
        try:
            # Get current count
            count_str = await cache.get(cache_key)
            current_count = int(count_str) if count_str else 0
            
            if current_count >= self.rate_limit:
                # Rate limit exceeded
                ttl_str = await cache.get(f"{cache_key}:ttl")
                reset_time = int(ttl_str) if ttl_str else self.window_size
                return False, 0, reset_time
            
            # Increment counter
            new_count = await cache.increment(cache_key)
            
            # Set expiration if this is the first request in the window
            if new_count == 1:
                await cache.expire(cache_key, self.window_size)
                await cache.set(
                    f"{cache_key}:ttl",
                    str(self.window_size),
                    self.window_size
                )
            
            remaining = max(0, self.rate_limit - new_count)
            return True, remaining, self.window_size
            
        except Exception:
            # If cache is unavailable, allow request but log warning
            return True, self.rate_limit, self.window_size
