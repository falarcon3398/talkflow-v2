import subprocess
from pathlib import Path
from app.config import settings

def run_musetalk(avatar_path: str, audio_path: str, job_id: str) -> str:
    """Stubbed run_musetalk for local development."""
    print(f"STUB: Lipsync skipped for {job_id}, using avatar image as video source")
    return avatar_path
