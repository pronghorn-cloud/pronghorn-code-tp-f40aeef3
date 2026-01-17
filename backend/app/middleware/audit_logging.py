"""Audit Logging Middleware

HIPAA-compliant audit logging for all API requests.
Logs PHI access and masks sensitive data.
"""

import time
import json
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


# PHI-related endpoints that require special logging
PHI_ENDPOINTS = [
    "/api/v1/claims",
    "/api/v1/documents",
]

# Fields to mask in logs
SENSITIVE_FIELDS = [
    "password",
    "token",
    "secret",
    "ssn",
    "patient_name",
    "patient_dob",
    "patient_address",
    "patient_phone",
    "patient_email",
]


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for HIPAA-compliant audit logging."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log audit information."""
        start_time = time.time()
        
        # Get correlation ID from request state
        correlation_id = getattr(request.state, "correlation_id", "unknown")
        
        # Determine if this is a PHI access
        is_phi_access = any(
            request.url.path.startswith(endpoint)
            for endpoint in PHI_ENDPOINTS
        )
        
        # Log request
        log_data = {
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", "unknown"),
            "phi_access": is_phi_access,
        }
        
        # Add user ID if authenticated
        if hasattr(request.state, "user_id"):
            log_data["user_id"] = str(request.state.user_id)
        
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            log_data.update({
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
            })
            
            # Log at appropriate level
            if response.status_code >= 500:
                logger.error("request_completed", **log_data)
            elif response.status_code >= 400:
                logger.warning("request_completed", **log_data)
            else:
                logger.info("request_completed", **log_data)
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            log_data.update({
                "status_code": 500,
                "duration_ms": round(duration * 1000, 2),
                "error": str(e),
            })
            logger.error("request_failed", **log_data)
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request, considering proxies."""
        # Check X-Forwarded-For header (set by load balancers/proxies)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP in the list
            return forwarded_for.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fall back to direct client IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _mask_sensitive_data(self, data: dict) -> dict:
        """Mask sensitive fields in data for logging."""
        if not isinstance(data, dict):
            return data
        
        masked = {}
        for key, value in data.items():
            if any(field in key.lower() for field in SENSITIVE_FIELDS):
                masked[key] = "***MASKED***"
            elif isinstance(value, dict):
                masked[key] = self._mask_sensitive_data(value)
            else:
                masked[key] = value
        
        return masked
