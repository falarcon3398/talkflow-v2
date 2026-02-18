import subprocess
from pathlib import Path
from app.config import settings

def enhance_video(video_path: str, job_id: str) -> str:
    """
    Wrapper for GFPGAN video enhancement.
    """
    output_dir = Path(settings.PROCESSING_DIR) / job_id
    enhanced_video = output_dir / "enhanced.mp4"
    
    cmd = [
        "python",
        f"{settings.MODELS_PATH}/GFPGAN/inference_gfpgan.py",
        "-i", video_path,
        "-o", str(enhanced_video),
        "--upscale", "2"
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except Exception as e:
        print(f"GFPGAN enhancement failed: {e}")
        return video_path # Stub fallback

    return str(enhanced_video)
