import os
from typing import List, Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Service Configuration
    ai_service_host: str = Field(default="localhost", env="AI_SERVICE_HOST")
    ai_service_port: int = Field(default=8001, env="AI_SERVICE_PORT")
    ai_service_workers: int = Field(default=4, env="AI_SERVICE_WORKERS")
    
    # GPU Configuration
    cuda_visible_devices: str = Field(default="0", env="CUDA_VISIBLE_DEVICES")
    use_gpu: bool = Field(default=True, env="USE_GPU")
    gpu_memory_fraction: float = Field(default=0.8, env="GPU_MEMORY_FRACTION")
    
    # Model Configuration
    model_base_path: str = Field(default="./models", env="MODEL_BASE_PATH")
    training_data_path: str = Field(default="./data/training", env="TRAINING_DATA_PATH")
    cache_dir: str = Field(default="./cache", env="CACHE_DIR")
    
    # Database Configuration
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    mongodb_url: str = Field(default="mongodb://localhost:27017/medimate_ai", env="MONGODB_URL")
    
    # MLflow Configuration
    mlflow_tracking_uri: str = Field(default="http://localhost:5000", env="MLFLOW_TRACKING_URI")
    mlflow_experiment_name: str = Field(default="medimate_ai_models", env="MLFLOW_EXPERIMENT_NAME")
    
    # Security
    secret_key: str = Field(default="dev-secret-key", env="SECRET_KEY")
    encryption_key: str = Field(default="dev-encryption-key", env="ENCRYPTION_KEY")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="./logs/ai_service.log", env="LOG_FILE")
    
    # Performance
    max_concurrent_requests: int = Field(default=10, env="MAX_CONCURRENT_REQUESTS")
    request_timeout: int = Field(default=300, env="REQUEST_TIMEOUT")
    batch_size: int = Field(default=32, env="BATCH_SIZE")
    
    # Medical Data Processing
    confidence_threshold: float = Field(default=0.85, env="CONFIDENCE_THRESHOLD")
    max_file_size_mb: int = Field(default=50, env="MAX_FILE_SIZE_MB")
    supported_formats: List[str] = Field(
        default=["pdf", "png", "jpg", "jpeg", "tiff"], 
        env="SUPPORTED_FORMATS"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        os.makedirs(self.model_base_path, exist_ok=True)
        os.makedirs(self.training_data_path, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)


# Global settings instance
settings = Settings()