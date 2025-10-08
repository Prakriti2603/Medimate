"""Health check endpoints for the AI service."""

import logging
import psutil
import time
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: datetime
    version: str
    uptime_seconds: float
    system_info: Dict[str, Any]
    gpu_info: Dict[str, Any] = None


# Track service start time
_start_time = time.time()


@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Comprehensive health check endpoint.
    Returns service status, system information, and GPU details if available.
    """
    try:
        current_time = time.time()
        uptime = current_time - _start_time
        
        # System information
        system_info = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
        }
        
        # GPU information (if available)
        gpu_info = None
        if settings.use_gpu:
            try:
                import torch
                if torch.cuda.is_available():
                    gpu_info = {
                        "available": True,
                        "device_count": torch.cuda.device_count(),
                        "current_device": torch.cuda.current_device(),
                        "device_name": torch.cuda.get_device_name(0),
                        "memory_allocated": torch.cuda.memory_allocated(0),
                        "memory_reserved": torch.cuda.memory_reserved(0)
                    }
                else:
                    gpu_info = {"available": False, "reason": "CUDA not available"}
            except ImportError:
                gpu_info = {"available": False, "reason": "PyTorch not installed"}
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now(),
            version="1.0.0",
            uptime_seconds=uptime,
            system_info=system_info,
            gpu_info=gpu_info
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.get("/ready")
async def readiness_check():
    """
    Readiness check endpoint for Kubernetes/Docker health checks.
    Returns simple status for load balancer health checks.
    """
    try:
        # Check if critical services are available
        # Add checks for database connections, model loading, etc.
        
        return {"status": "ready", "timestamp": datetime.now()}
        
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")


@router.get("/live")
async def liveness_check():
    """
    Liveness check endpoint for Kubernetes/Docker health checks.
    Simple endpoint to verify the service is running.
    """
    return {"status": "alive", "timestamp": datetime.now()}