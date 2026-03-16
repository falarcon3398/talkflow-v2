from app.core.pipeline import tts, lipsync, enhance
from app.core.storage.minio_client import minio_client
from app.models.job import Job
from app.database import SessionLocal
import subprocess
import shutil
import logging
from pathlib import Path
from app.config import settings

logger = logging.getLogger(__name__)

def update_job_status(job_id: str, status: str = None, progress: int = None, result_url: str = None, error_message: str = None):
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            if status: job.status = status
            if progress is not None: job.progress = progress
            if result_url: job.result_url = result_url
            if error_message: job.error_message = error_message
            db.commit()
    finally:
        db.close()

def cleanup_job_data(job_id: str):
    """Purge temporary processing data for a specific job."""
    try:
        proc_dir = Path(settings.PROCESSING_DIR) / job_id
        if proc_dir.exists():
            shutil.rmtree(str(proc_dir))
            logger.info(f"Cleaned up processing data for job {job_id}")
    except Exception as e:
        logger.warning(f"Failed to cleanup processing data for {job_id}: {e}")

def apply_aspect_ratio(input_path: str, output_path: str, aspect_ratio: str) -> str:
    """
    Use ffmpeg to crop/pad the video to the target aspect ratio.
    - 16:9  → 1920x1080 (landscape, black bars if needed)
    - 9:16  → 1080x1920 (portrait / TikTok / Reels)
    Returns output_path on success, input_path as fallback.
    """
    try:
        if aspect_ratio == "9:16":
            # Scale to height 1920 keeping aspect, then crop width to 1080
            vf = "scale=-2:1920,crop=1080:1920:(iw-1080)/2:0"
            target_w, target_h = 1080, 1920
        else:  # 16:9 default
            # Scale to width 1920 keeping aspect, then crop height to 1080
            vf = "scale=1920:-2,crop=1920:1080:0:(ih-1080)/2"
            target_w, target_h = 1920, 1080

        cmd = [
            "ffmpeg", "-y",
            "-i", str(input_path),
            "-vf", vf,
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k",
            str(output_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            logger.info(f"Applied {aspect_ratio} ({target_w}x{target_h}) to {output_path}")
            return str(output_path)
        else:
            logger.warning(f"ffmpeg aspect ratio failed: {result.stderr[-300:]}")
            return input_path
    except Exception as e:
        logger.warning(f"apply_aspect_ratio error (skipping): {e}")
        return input_path


def run_text_to_video_pipeline(job_id, avatar_image_path, text, voice_id, resolution, speaker_wav_path=None, aspect_ratio="16:9", language="en"):
    try:
        update_job_status(job_id, status="processing", progress=10)
        
        # 1. TTS
        audio_path = tts.generate_speech(text, voice_id, job_id, speaker_wav_path, language=language)
        update_job_status(job_id, progress=30)
        
        # 2. Lip Sync
        raw_video = lipsync.run_inference(avatar_image_path, audio_path, job_id)
        update_job_status(job_id, progress=70)
        
        # 3. Enhance
        final_video = enhance.enhance_video(raw_video, job_id)
        update_job_status(job_id, progress=85)
        
        # 4. Apply Aspect Ratio (crop/pad with ffmpeg)
        raw_video_path = Path(raw_video)
        final_filename = f"{job_id}.mp4"
        dest_path = Path(settings.OUTPUT_DIR) / final_filename
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        if raw_video_path.exists():
            # Apply aspect ratio crop — output directly to dest_path
            result_path = apply_aspect_ratio(str(raw_video_path), str(dest_path), aspect_ratio)
            if result_path != str(dest_path) and raw_video_path.exists():
                # ffmpeg failed or skipped — just copy the raw video
                shutil.copy(str(raw_video_path), str(dest_path))
        
        update_job_status(job_id, status="completed", progress=100, result_url=f"/api/v1/jobs/{job_id}/download")
        cleanup_job_data(job_id)
        
    except Exception as e:
        update_job_status(job_id, status="failed", error_message=str(e))
        raise


def run_audio_to_video_pipeline(job_id, avatar_image_path, audio_file_path, enable_enhance):
    try:
        update_job_status(job_id, status="processing", progress=10)
        
        # 1. Lip Sync
        raw_video = lipsync.run_inference(avatar_image_path, audio_file_path, job_id)
        update_job_status(job_id, progress=70)
        
        # 2. Enhance
        if enable_enhance:
            final_video = enhance.enhance_video(raw_video, job_id)
        update_job_status(job_id, progress=90)
        
        # 3. Final Finalize
        final_video_path = Path(raw_video)
        final_filename = f"{job_id}.mp4"
        dest_path = Path(settings.OUTPUT_DIR) / final_filename
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        if final_video_path.exists() and str(final_video_path) != str(dest_path):
            shutil.copy(str(final_video_path), str(dest_path))
        
        update_job_status(job_id, status="completed", progress=100, result_url=f"/api/v1/jobs/{job_id}/download")
        cleanup_job_data(job_id)
        
    except Exception as e:
        update_job_status(job_id, status="failed", error_message=str(e))
        raise
