from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "TalkFlow"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql://talkflow:changeme@postgres:5432/talkflow"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # Storage
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    MINIO_BUCKET: str = "talkflow"
    
    # Paths
    MODELS_PATH: str = "/app/models"
    UPLOAD_DIR: str = "/app/data/uploads"
    PROCESSING_DIR: str = "/app/data/processing"
    OUTPUT_DIR: str = "/app/data/outputs"

    class Config:
        env_file = ".env"

settings = Settings()
