import subprocess
import os
import logging
from pathlib import Path
from app.config import settings

logger = logging.getLogger(__name__)

def enhance_video(video_path: str, job_id: str) -> str:
    """Enhanced face using GFPGAN via external script for VRAM isolation."""
    try:
        input_path = Path(video_path)
        if not input_path.exists():
            logger.error(f"Input video not found: {video_path}")
            return video_path

        output_path = input_path.parent / f"{job_id}_enhanced.mp4"
        model_path = Path(settings.MODELS_PATH) / "gfpgan" / "weights" / "GFPGANv1.4.pth"
        enhance_script = Path(settings.BASE_DIR) / "scripts" / "face_enhance.py"

        if not model_path.exists():
            logger.warning(f"GFPGAN model not found at {model_path}. Skipping enhancement.")
            return video_path

        # Construct command
        import sys
        cmd = [
            sys.executable, str(enhance_script),
            "--input", str(input_path),
            "--output", str(output_path),
            "--model_path", str(model_path),
            "--upscale", "1"
        ]

        logger.info(f"Running enhancement for {job_id}...")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            logger.info(f"Enhancement successful: {output_path}")
            return str(output_path)
        else:
            logger.error(f"Enhancement failed (exit {result.returncode}): {result.stderr}")
            return video_path

    except Exception as e:
        logger.error(f"Unexpected error in enhancement step: {e}")
        return video_path
