import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

# Base directory
_BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "TalkFlow"
    API_V1_STR: str = "/api/v1"
    BASE_DIR: str = str(_BASE_DIR)
    
    # Check if running on Vercel
    IS_VERCEL: bool = os.environ.get("VERCEL") == "1"
    
    # Database
    DATABASE_URL: str = (
        "sqlite:////tmp/talkflow.db" 
        if os.environ.get("VERCEL") == "1" 
        else f"sqlite:///{_BASE_DIR}/talkflow.db"
    )
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Storage (Local for now)
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    MINIO_BUCKET: str = "talkflow"
    
    # Paths (Relative to BASE_DIR)
    MODELS_PATH: str = str(_BASE_DIR.parent / "models")
    STATIC_DIR: str = str(_BASE_DIR / "app" / "static")
    MUSETALK_DIR: str = str(_BASE_DIR / "musetalk")
    SADTALKER_DIR: str = "/Users/iblstudios/local_sadtalker_test/SadTalker"
    SADTALKER_VENV_PYTHON: str = "/Users/iblstudios/local_sadtalker_test/SadTalker/.venv/bin/python"
    LIPSYNC_ENGINE: str = "sadtalker" # options: "musetalk", "sadtalker"
    
    UPLOAD_DIR: str = "/tmp/uploads" if IS_VERCEL else str(_BASE_DIR / "uploads")
    PROCESSING_DIR: str = "/tmp/processing" if IS_VERCEL else str(_BASE_DIR / "processing")
    OUTPUT_DIR: str = "/tmp/outputs" if IS_VERCEL else str(_BASE_DIR / "outputs")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
