import logging
from pathlib import Path
from app.config import settings
from app.core.pipeline_adapters.musetalk_adapter import musetalk_adapter

logger = logging.getLogger(__name__)

def run_musetalk(avatar_path: str, audio_path: str, job_id: str) -> str:
    """Runs the real MuseTalk lip-sync or falls back to static if models are missing."""
    logger.info(f"Initiating MuseTalk lip-sync for job {job_id}")
    
    result_path = musetalk_adapter.run_inference(avatar_path, audio_path, job_id)
    
    if result_path and Path(result_path).exists():
        return result_path
    
    logger.warning(f"MuseTalk failed or skipped for {job_id}, falling back to static image")
    return avatar_path
