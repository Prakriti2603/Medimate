"""
MediMate AI Service - Main Application Entry Point
Provides AI-powered medical document processing and form auto-fill capabilities.
"""

import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from config.settings import settings
from core.logging_config import setup_logging
from api.routes import document_processing, model_management, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting MediMate AI Service...")
    
    # Initialize GPU if available
    if settings.use_gpu:
        try:
            import torch
            if torch.cuda.is_available():
                logger.info(f"GPU available: {torch.cuda.get_device_name(0)}")
                os.environ["CUDA_VISIBLE_DEVICES"] = settings.cuda_visible_devices
            else:
                logger.warning("GPU requested but not available, falling back to CPU")
        except ImportError:
            logger.warning("PyTorch not available, using CPU only")
    
    # Initialize MLflow
    try:
        import mlflow
        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
        mlflow.set_experiment(settings.mlflow_experiment_name)
        logger.info(f"MLflow initialized with tracking URI: {settings.mlflow_tracking_uri}")
    except Exception as e:
        logger.error(f"Failed to initialize MLflow: {e}")
    
    logger.info("MediMate AI Service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down MediMate AI Service...")


# Create FastAPI application
app = FastAPI(
    title="MediMate AI Service",
    description="AI-powered medical document processing and form auto-fill service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", settings.ai_service_host]
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(document_processing.router, prefix="/api/v1/documents", tags=["Document Processing"])
app.include_router(model_management.router, prefix="/api/v1/models", tags=["Model Management"])


@app.get("/")
async def root():
    """Root endpoint providing service information."""
    return {
        "service": "MediMate AI Service",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.ai_service_host,
        port=settings.ai_service_port,
        workers=settings.ai_service_workers,
        log_level=settings.log_level.lower(),
        reload=False
    )