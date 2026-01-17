"""API v1 Router

Main router that includes all API endpoints.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    claims,
    documents,
    forms,
    rules,
    ahcip,
    audit,
    users,
)

api_router = APIRouter()

# Authentication endpoints
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

# User management endpoints
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

# Claims endpoints
api_router.include_router(
    claims.router,
    prefix="/claims",
    tags=["Claims"]
)

# Document endpoints
api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["Documents"]
)

# Form and template endpoints
api_router.include_router(
    forms.router,
    prefix="/forms",
    tags=["Forms & Templates"]
)

# Rules engine endpoints
api_router.include_router(
    rules.router,
    prefix="/rules",
    tags=["Rules Engine"]
)

# AHCIP code lookup endpoints
api_router.include_router(
    ahcip.router,
    prefix="/ahcip-codes",
    tags=["AHCIP Codes"]
)

# Audit and compliance endpoints
api_router.include_router(
    audit.router,
    prefix="/audit",
    tags=["Audit & Compliance"]
)
