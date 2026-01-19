"""API routers."""
from fastapi import APIRouter
from app.api import health, auth, documents, search, chat

# Create main API router
api_router = APIRouter()

# Include routers
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(documents.router)
api_router.include_router(search.router)
api_router.include_router(chat.router)