"""Request Correlation Middleware

Adds correlation IDs to requests for distributed tracing.
"""

import uuid
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


CORRELATION_ID_HEADER = "X-Correlation-ID"
REQUEST_ID_HEADER = "X-Request-ID"


class RequestCorrelationMiddleware(BaseHTTPMiddleware):
    """Middleware for request correlation and tracing."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add correlation ID to request and response."""
        # Get or generate correlation ID
        correlation_id = request.headers.get(
            CORRELATION_ID_HEADER,
            str(uuid.uuid4())
        )
        
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Store in request state for use by other middleware and handlers
        request.state.correlation_id = correlation_id
        request.state.request_id = request_id
        
        # Process request
        response = await call_next(request)
        
        # Add headers to response
        response.headers[CORRELATION_ID_HEADER] = correlation_id
        response.headers[REQUEST_ID_HEADER] = request_id
        
        return response
