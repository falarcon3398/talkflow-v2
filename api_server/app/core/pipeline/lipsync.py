import subprocess
from pathlib import Path
from app.config import settings

def run_musetalk(avatar_path: str, audio_path: str, job_id: str) -> str:
    """
    Wrapper for MuseTalk lip sync.
    """
    output_dir = Path(settings.PROCESSING_DIR) / job_id
    output_video = output_dir / "lipsync_raw.mp4"
    
    # MuseTalk inference command
    cmd = [
        "python",
        f"{settings.MODELS_PATH}/MuseTalk/inference.py",
        "--driven_audio", audio_path,
        "--source_image", avatar_path,
        "--result_dir", str(output_dir),
        "--fps", "30"
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except Exception as e:
        # For development, if MuseTalk isn't fully installed yet
        print(f"MuseTalk lip sync failed or not installed: {e}")
        # Placeholder for MVP testing without GPU
        return avatar_path # Return input if failed for now (stub)

    return str(output_video)
