import logging
import threading
from pathlib import Path
from app.config import settings
from app.core.pipeline_adapters.musetalk_adapter import musetalk_adapter
from app.core.pipeline_adapters.sadtalker_adapter import sadtalker_adapter

logger = logging.getLogger(__name__)
lipsync_lock = threading.Lock()

def run_inference(avatar_path: str, audio_path: str, job_id: str) -> str:
    """Dispatches the lip-sync task to the configured engine with a sequential lock."""
    with lipsync_lock:
        engine = settings.LIPSYNC_ENGINE.lower()
        logger.info(f"Initiating {engine} lip-sync for job {job_id} (Lock acquired)")
        
        if engine == "sadtalker":
            result_path = sadtalker_adapter.run_inference(avatar_path, audio_path, job_id)
        else:
            # Default to MuseTalk
            result_path = musetalk_adapter.run_inference(avatar_path, audio_path, job_id)
        
        if result_path and Path(result_path).exists():
            return result_path
        
        logger.warning(f"{engine} failed or skipped for {job_id}, falling back to static image")
        return avatar_path

# Keep for backward compatibility if needed by orchestration
def run_musetalk(avatar_path: str, audio_path: str, job_id: str) -> str:
    return run_inference(avatar_path, audio_path, job_id)
