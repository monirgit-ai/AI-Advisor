"""Health check endpoints."""
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(prefix="")


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: Service status and information
    """
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }
