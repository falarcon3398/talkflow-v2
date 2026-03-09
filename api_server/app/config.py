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
    DATABASE_URL: str = os.environ.get(
        "DATABASE_URL",
        "sqlite:////tmp/talkflow.db" if os.environ.get("VERCEL") == "1" else f"sqlite:///{_BASE_DIR}/talkflow.db"
    )
    
    # Redis
    REDIS_URL: str = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    
    # Storage
    MINIO_ENDPOINT: str = os.environ.get("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.environ.get("MINIO_SECRET_KEY", "minioadmin")
    MINIO_SECURE: bool = os.environ.get("MINIO_SECURE", "False").lower() == "true"
    MINIO_BUCKET: str = os.environ.get("MINIO_BUCKET", "talkflow")
    
    # Paths (Relative to BASE_DIR unless absolute)
    MODELS_PATH: str = os.environ.get("MODELS_PATH", str(_BASE_DIR.parent / "models"))
    STATIC_DIR: str = os.environ.get("STATIC_DIR", str(_BASE_DIR / "app" / "static"))
    MUSETALK_DIR: str = os.environ.get("MUSETALK_DIR", str(_BASE_DIR / "musetalk"))
    
    # LipSync Engines
    LIPSYNC_ENGINE: str = os.environ.get("LIPSYNC_ENGINE", "musetalk")
    SADTALKER_DIR: Optional[str] = os.environ.get("SADTALKER_DIR")
    SADTALKER_VENV_PYTHON: Optional[str] = os.environ.get("SADTALKER_VENV_PYTHON")
    
    UPLOAD_DIR: str = os.environ.get("UPLOAD_DIR", "/tmp/uploads" if IS_VERCEL else str(_BASE_DIR / "uploads"))
    PROCESSING_DIR: str = os.environ.get("PROCESSING_DIR", "/tmp/processing" if IS_VERCEL else str(_BASE_DIR / "processing"))
    OUTPUT_DIR: str = os.environ.get("OUTPUT_DIR", "/tmp/outputs" if IS_VERCEL else str(_BASE_DIR / "outputs"))

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
