import subprocess
from pathlib import Path
from app.config import settings

def enhance_video(video_path: str, job_id: str) -> str:
    """Stubbed enhance_video for local development."""
    print(f"STUB: Enhancement skipped for {job_id}, using {video_path}")
    return video_path
