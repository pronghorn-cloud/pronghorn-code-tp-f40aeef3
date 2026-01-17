"""Main FastAPI Application Entry Point

Claims Processing Platform API
- Digital claims submission and tracking
- Automated adjudication via rules engine
- Document management
- AHCIP code lookup
- Compliance & audit reporting
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.router import api_router
from app.middleware.audit_logging import AuditLoggingMiddleware
from app.middleware.request_correlation import RequestCorrelationMiddleware
from app.middleware.rate_limiting import RateLimitingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    print(f"Starting Claims Processing Platform v{settings.VERSION}")
    # Create database tables (in production, use Alembic migrations)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Shutdown
    print("Shutting down Claims Processing Platform")


# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Claims Processing Platform API - Healthcare claims management system",
    version=settings.VERSION,
    docs_url="/api/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/api/redoc" if settings.ENVIRONMENT != "production" else None,
    openapi_url="/api/openapi.json" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Add GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add custom middleware
app.add_middleware(RequestCorrelationMiddleware)
app.add_middleware(AuditLoggingMiddleware)
app.add_middleware(RateLimitingMiddleware)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancer and container orchestration."""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "documentation": "/api/docs",
        "health": "/health"
    }
