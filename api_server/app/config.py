import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "TalkFlow"
    API_V1_STR: str = "/api/v1"
    
    # Check if running on Vercel
    IS_VERCEL: bool = os.environ.get("VERCEL") == "1"
    
    # Database
    DATABASE_URL: str = "sqlite:////tmp/talkflow.db" if os.environ.get("VERCEL") == "1" else "sqlite:///./talkflow.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Storage (Local for now)
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    MINIO_BUCKET: str = "talkflow"
    
    # Paths (Local)
    MODELS_PATH: str = "./models"
    UPLOAD_DIR: str = "/tmp/uploads" if os.environ.get("VERCEL") == "1" else "./uploads"
    PROCESSING_DIR: str = "/tmp/processing" if os.environ.get("VERCEL") == "1" else "./processing"
    OUTPUT_DIR: str = "/tmp/outputs" if os.environ.get("VERCEL") == "1" else "./outputs"

    class Config:
        env_file = ".env"

settings = Settings()
