"""CSRF Protection Middleware

Cross-Site Request Forgery protection for state-changing operations.
"""

import secrets
import hmac
import hashlib
from typing import Callable, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

from app.core.config import settings
from app.core.cache import cache, CacheKeys


class CSRFMiddleware(BaseHTTPMiddleware):
    """Middleware for CSRF token validation."""
    
    # Methods that require CSRF protection
    PROTECTED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
    
    # Header name for CSRF token
    CSRF_HEADER = "X-CSRF-Token"
    CSRF_COOKIE = "csrf_token"
    
    def __init__(self, app, secret_key: str = None, exempt_paths: list = None):
        super().__init__(app)
        self.secret_key = secret_key or settings.SECRET_KEY
        self.exempt_paths = exempt_paths or [
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/refresh",
            "/health",
            "/",
            "/docs",
            "/openapi.json",
        ]
        self.token_length = 32
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Validate CSRF token for protected methods."""
        # Skip CSRF for safe methods
        if request.method not in self.PROTECTED_METHODS:
            response = await call_next(request)
            # Set CSRF cookie on GET requests
            if request.method == "GET":
                response = await self._set_csrf_cookie(request, response)
            return response
        
        # Skip CSRF for exempt paths
        if self._is_exempt(request.url.path):
            return await call_next(request)
        
        # Skip CSRF for API key authenticated requests
        if request.headers.get("X-API-Key"):
            return await call_next(request)
        
        # Validate CSRF token
        if not await self._validate_csrf_token(request):
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "CSRF token missing or invalid",
                    "code": "CSRF_VALIDATION_FAILED",
                }
            )
        
        return await call_next(request)
    
    def _is_exempt(self, path: str) -> bool:
        """Check if path is exempt from CSRF validation."""
        for exempt_path in self.exempt_paths:
            if path.startswith(exempt_path):
                return True
        return False
    
    async def _validate_csrf_token(self, request: Request) -> bool:
        """Validate CSRF token from header against cookie."""
        # Get token from header
        header_token = request.headers.get(self.CSRF_HEADER)
        if not header_token:
            return False
        
        # Get token from cookie
        cookie_token = request.cookies.get(self.CSRF_COOKIE)
        if not cookie_token:
            return False
        
        # Verify tokens match using constant-time comparison
        try:
            return hmac.compare_digest(header_token, cookie_token)
        except Exception:
            return False
    
    async def _set_csrf_cookie(self, request: Request, response: Response) -> Response:
        """Set CSRF token cookie if not present."""
        existing_token = request.cookies.get(self.CSRF_COOKIE)
        
        if not existing_token:
            # Generate new token
            token = self._generate_token()
            response.set_cookie(
                key=self.CSRF_COOKIE,
                value=token,
                httponly=False,  # Needs to be readable by JavaScript
                secure=settings.ENVIRONMENT == "production",
                samesite="strict",
                max_age=86400,  # 24 hours
            )
        
        return response
    
    def _generate_token(self) -> str:
        """Generate a secure CSRF token."""
        return secrets.token_urlsafe(self.token_length)
    
    def _create_signed_token(self, token: str) -> str:
        """Create a signed version of the token."""
        signature = hmac.new(
            self.secret_key.encode(),
            token.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"{token}.{signature}"
    
    def _verify_signed_token(self, signed_token: str) -> Optional[str]:
        """Verify and extract token from signed token."""
        try:
            parts = signed_token.rsplit(".", 1)
            if len(parts) != 2:
                return None
            
            token, signature = parts
            expected_signature = hmac.new(
                self.secret_key.encode(),
                token.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if hmac.compare_digest(signature, expected_signature):
                return token
            return None
        except Exception:
            return None


class DoubleSubmitCSRFMiddleware(CSRFMiddleware):
    """Enhanced CSRF middleware using double-submit cookie pattern."""
    
    async def _validate_csrf_token(self, request: Request) -> bool:
        """Validate using double-submit cookie pattern with signed tokens."""
        header_token = request.headers.get(self.CSRF_HEADER)
        cookie_token = request.cookies.get(self.CSRF_COOKIE)
        
        if not header_token or not cookie_token:
            return False
        
        # Verify both tokens are valid signed tokens
        header_payload = self._verify_signed_token(header_token)
        cookie_payload = self._verify_signed_token(cookie_token)
        
        if not header_payload or not cookie_payload:
            return False
        
        # Compare payloads
        return hmac.compare_digest(header_payload, cookie_payload)
    
    async def _set_csrf_cookie(self, request: Request, response: Response) -> Response:
        """Set signed CSRF token cookie."""
        existing_token = request.cookies.get(self.CSRF_COOKIE)
        
        if not existing_token or not self._verify_signed_token(existing_token):
            token = self._generate_token()
            signed_token = self._create_signed_token(token)
            
            response.set_cookie(
                key=self.CSRF_COOKIE,
                value=signed_token,
                httponly=False,
                secure=settings.ENVIRONMENT == "production",
                samesite="strict",
                max_age=86400,
            )
        
        return response
