"""Input Sanitization Middleware

Sanitizes and validates incoming request data to prevent injection attacks.
"""

import re
import html
import json
from typing import Callable, Any, Dict, List, Union
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

from app.core.config import settings


class InputSanitizationMiddleware(BaseHTTPMiddleware):
    """Middleware for sanitizing input data."""
    
    # Patterns that indicate potential SQL injection
    SQL_INJECTION_PATTERNS = [
        r"(\s|^)(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|CREATE|TRUNCATE)(\s|$)",
        r"(--)|(;\s*$)",
        r"(\s|^)(OR|AND)(\s+)\d+(\s*)=(\s*)\d+",
        r"'"
        r"(\s*)OR(\s*)'",
    ]
    
    # Patterns that indicate potential XSS
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
        r"<link[^>]*>",
        r"expression\s*\(",
    ]
    
    # Maximum field lengths
    MAX_STRING_LENGTH = 10000
    MAX_FIELD_NAME_LENGTH = 100
    MAX_NESTING_DEPTH = 10
    
    def __init__(
        self,
        app,
        sanitize_html: bool = True,
        check_sql_injection: bool = True,
        check_xss: bool = True,
        max_body_size: int = None,
    ):
        super().__init__(app)
        self.sanitize_html = sanitize_html
        self.check_sql_injection = check_sql_injection
        self.check_xss = check_xss
        self.max_body_size = max_body_size or 10 * 1024 * 1024  # 10MB default
        
        # Compile regex patterns for performance
        self.sql_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.SQL_INJECTION_PATTERNS
        ]
        self.xss_patterns = [
            re.compile(p, re.IGNORECASE | re.DOTALL) for p in self.XSS_PATTERNS
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Sanitize request data before processing."""
        # Skip sanitization for certain paths
        if self._should_skip(request):
            return await call_next(request)
        
        # Check content length
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_body_size:
            return JSONResponse(
                status_code=413,
                content={
                    "detail": "Request body too large",
                    "max_size": self.max_body_size,
                }
            )
        
        # Sanitize query parameters
        sanitization_error = self._check_query_params(request)
        if sanitization_error:
            return JSONResponse(
                status_code=400,
                content={
                    "detail": "Invalid input detected",
                    "error": sanitization_error,
                }
            )
        
        # For POST/PUT/PATCH, sanitize body
        if request.method in {"POST", "PUT", "PATCH"}:
            content_type = request.headers.get("content-type", "")
            
            if "application/json" in content_type:
                try:
                    body = await request.body()
                    if body:
                        data = json.loads(body)
                        sanitization_error = self._validate_data(data)
                        
                        if sanitization_error:
                            return JSONResponse(
                                status_code=400,
                                content={
                                    "detail": "Invalid input detected",
                                    "error": sanitization_error,
                                }
                            )
                except json.JSONDecodeError:
                    return JSONResponse(
                        status_code=400,
                        content={"detail": "Invalid JSON body"}
                    )
        
        return await call_next(request)
    
    def _should_skip(self, request: Request) -> bool:
        """Check if request should skip sanitization."""
        skip_paths = ["/health", "/docs", "/openapi.json", "/redoc"]
        return any(request.url.path.startswith(p) for p in skip_paths)
    
    def _check_query_params(self, request: Request) -> str | None:
        """Validate query parameters."""
        for key, value in request.query_params.items():
            if len(key) > self.MAX_FIELD_NAME_LENGTH:
                return f"Query parameter name too long: {key[:20]}..."
            
            if len(value) > self.MAX_STRING_LENGTH:
                return f"Query parameter value too long: {key}"
            
            error = self._check_string(value)
            if error:
                return f"Invalid query parameter '{key}': {error}"
        
        return None
    
    def _validate_data(
        self,
        data: Any,
        depth: int = 0,
        path: str = "root"
    ) -> str | None:
        """Recursively validate and check data for malicious content."""
        if depth > self.MAX_NESTING_DEPTH:
            return f"Maximum nesting depth exceeded at {path}"
        
        if isinstance(data, dict):
            for key, value in data.items():
                # Validate key
                if not isinstance(key, str):
                    return f"Invalid key type at {path}"
                
                if len(key) > self.MAX_FIELD_NAME_LENGTH:
                    return f"Field name too long at {path}.{key[:20]}..."
                
                # Check key for injection patterns
                key_error = self._check_string(key)
                if key_error:
                    return f"Invalid field name at {path}: {key_error}"
                
                # Recursively validate value
                value_error = self._validate_data(
                    value,
                    depth + 1,
                    f"{path}.{key}"
                )
                if value_error:
                    return value_error
                    
        elif isinstance(data, list):
            for i, item in enumerate(data):
                error = self._validate_data(item, depth + 1, f"{path}[{i}]")
                if error:
                    return error
                    
        elif isinstance(data, str):
            if len(data) > self.MAX_STRING_LENGTH:
                return f"String too long at {path}"
            
            error = self._check_string(data)
            if error:
                return f"Invalid content at {path}: {error}"
        
        return None
    
    def _check_string(self, value: str) -> str | None:
        """Check string for malicious patterns."""
        if self.check_sql_injection:
            for pattern in self.sql_patterns:
                if pattern.search(value):
                    return "Potential SQL injection detected"
        
        if self.check_xss:
            for pattern in self.xss_patterns:
                if pattern.search(value):
                    return "Potential XSS detected"
        
        return None
    
    def sanitize_string(self, value: str) -> str:
        """Sanitize a string value."""
        if self.sanitize_html:
            value = html.escape(value)
        
        # Remove null bytes
        value = value.replace("\x00", "")
        
        # Normalize unicode
        value = value.encode("utf-8", errors="ignore").decode("utf-8")
        
        return value
    
    def sanitize_data(self, data: Any) -> Any:
        """Recursively sanitize data."""
        if isinstance(data, dict):
            return {
                self.sanitize_string(k): self.sanitize_data(v)
                for k, v in data.items()
            }
        elif isinstance(data, list):
            return [self.sanitize_data(item) for item in data]
        elif isinstance(data, str):
            return self.sanitize_string(data)
        else:
            return data


class SQLInjectionFilter:
    """Specialized filter for SQL injection prevention."""
    
    DANGEROUS_KEYWORDS = {
        "SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "UNION",
        "ALTER", "CREATE", "TRUNCATE", "EXEC", "EXECUTE",
        "XP_", "SP_", "0X", "CHAR(", "NCHAR(", "VARCHAR(",
        "CAST(", "CONVERT(", "TABLE", "FROM", "WHERE",
    }
    
    @classmethod
    def is_safe(cls, value: str) -> bool:
        """Check if value is safe from SQL injection."""
        upper_value = value.upper()
        
        # Check for dangerous keywords
        for keyword in cls.DANGEROUS_KEYWORDS:
            if keyword in upper_value:
                # Additional context check - is it actually dangerous?
                pattern = rf"(^|\s|;){re.escape(keyword)}(\s|$|;|\()"
                if re.search(pattern, upper_value):
                    return False
        
        # Check for comment sequences
        if "--" in value or "/*" in value:
            return False
        
        # Check for hex encoding
        if re.search(r"0x[0-9a-fA-F]+", value):
            return False
        
        return True


class XSSFilter:
    """Specialized filter for XSS prevention."""
    
    @classmethod
    def sanitize(cls, value: str) -> str:
        """Sanitize string to prevent XSS."""
        # HTML encode special characters
        value = html.escape(value)
        
        # Remove any remaining script-like content
        value = re.sub(r"javascript:", "", value, flags=re.IGNORECASE)
        value = re.sub(r"on\w+=", "", value, flags=re.IGNORECASE)
        
        return value
    
    @classmethod
    def is_safe(cls, value: str) -> bool:
        """Check if value is safe from XSS."""
        dangerous_patterns = [
            r"<script",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe",
            r"<object",
            r"<embed",
            r"expression\s*\(",
            r"url\s*\(",
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return False
        
        return True
