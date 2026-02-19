from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "TalkFlow"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite:///./talkflow.db"
    
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
    UPLOAD_DIR: str = "./uploads"
    PROCESSING_DIR: str = "./processing"
    OUTPUT_DIR: str = "./outputs"

    class Config:
        env_file = ".env"

settings = Settings()
