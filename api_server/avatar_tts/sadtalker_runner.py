import subprocess
import os
import time
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Configured path from user request
SADTALKER_DIR = Path("/Users/iblstudios/local_sadtalker_test/SadTalker")
SADTALKER_VENV_PYTHON = SADTALKER_DIR / ".venv" / "bin" / "python"

def run_sadtalker(image_path, audio_path):
    """
    Executes SadTalker inference via CLI using the specified installation.
    """
    if not SADTALKER_DIR.exists():
        raise FileNotFoundError(f"SadTalker installation not found at: {SADTALKER_DIR}")

    timestamp = int(time.time())
    # Subfolder for this specific generation to avoid overlap
    job_result_dir = Path(__file__).parent / "outputs" / "videos" / str(timestamp)
    job_result_dir.mkdir(parents=True, exist_ok=True)

    # Final destination for the single mp4 we want to return
    final_output_dir = Path(__file__).parent / "outputs" / "videos"
    final_output_path = final_output_dir / f"{timestamp}_final.mp4"

    cmd = [
        str(SADTALKER_VENV_PYTHON),
        str(SADTALKER_DIR / "inference.py"),
        "--source_image", os.path.abspath(image_path),
        "--driven_audio", os.path.abspath(audio_path),
        "--result_dir", os.path.abspath(job_result_dir),
        "--still",
        "--preprocess", "crop",
        "--size", "256",
        "--cpu"
    ]

    logger.info(f"Running SadTalker command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(SADTALKER_DIR),
            capture_output=True,
            text=True,
            check=True
        )
        logger.info("SadTalker completed successfully.")
        
        # SadTalker saves to {result_dir}/{timestamp}/*.mp4
        # We find the generated video and move it to the parent outputs/videos/
        generated_videos = list(job_result_dir.rglob("*.mp4"))
        if not generated_videos:
            logger.error(f"No video found in {job_result_dir}")
            return None
        
        # Take the first (and usually only) mp4
        video_source = generated_videos[0]
        import shutil
        shutil.move(str(video_source), str(final_output_path))
        
        return str(final_output_path)

    except subprocess.CalledProcessError as e:
        logger.error(f"SadTalker CLI failed (code {e.returncode}): {e.stderr}")
        raise RuntimeError(f"SadTalker failed: {e.stderr}")
