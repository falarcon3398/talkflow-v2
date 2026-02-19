from app.core.pipeline import tts, lipsync, enhance
from app.core.storage.minio_client import minio_client
from app.models.job import Job
from app.database import SessionLocal
import subprocess
import shutil
from pathlib import Path
from app.config import settings

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

def run_text_to_video_pipeline(job_id, avatar_image_path, text, voice_id, resolution):
    try:
        update_job_status(job_id, status="processing", progress=10)
        
        # 1. TTS
        audio_path = tts.generate_speech(text, voice_id, job_id)
        update_job_status(job_id, progress=30)
        
        # 2. Lip Sync
        raw_video = lipsync.run_musetalk(avatar_image_path, audio_path, job_id)
        update_job_status(job_id, progress=70)
        
        # 3. Enhance
        final_video = enhance.enhance_video(raw_video, job_id)
        update_job_status(job_id, progress=90)
        
        # Dest path
        final_filename = f"{job_id}.mp4"
        dest_path = Path(settings.OUTPUT_DIR) / final_filename
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # In MVP local mode, use FFmpeg to create a video from the image and generated audio
        if Path(avatar_image_path).exists():
            try:
                # Loop image for the duration of the audio
                process = subprocess.run([
                    "ffmpeg", "-y", "-loop", "1", "-i", str(avatar_image_path),
                    "-i", str(audio_path),
                    "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac", 
                    "-b:a", "192k", "-pix_fmt", "yuv420p", "-shortest",
                    "-t", "60", # Safety limit
                    "-vf", "scale=1280:720", 
                    str(dest_path)
                ], capture_output=True, text=True, timeout=30)
                
                if process.returncode != 0:
                    print(f"ERROR: FFmpeg failed in text-to-video with return code {process.returncode}")
                    print(f"FFmpeg stderr: {process.stderr}")
                    shutil.copy(avatar_image_path, dest_path)
            except Exception as e:
                print(f"ERROR: Exception during FFmpeg execution in text-to-video: {str(e)}")
                shutil.copy(avatar_image_path, dest_path)
        
        update_job_status(job_id, status="completed", progress=100, result_url=f"/api/v1/jobs/{job_id}/download")
        
    except Exception as e:
        update_job_status(job_id, status="failed", error_message=str(e))
        raise

def run_audio_to_video_pipeline(job_id, avatar_image_path, audio_file_path, enable_enhance):
    try:
        update_job_status(job_id, status="processing", progress=10)
        
        # 1. Lip Sync (Stubbed)
        # In real mode, use audio_file_path directly
        raw_video = lipsync.run_musetalk(avatar_image_path, audio_file_path, job_id)
        update_job_status(job_id, progress=70)
        
        # 2. Enhance
        if enable_enhance:
            final_video = enhance.enhance_video(raw_video, job_id)
        update_job_status(job_id, progress=90)
        
        # Dest path
        final_filename = f"{job_id}.mp4"
        dest_path = Path(settings.OUTPUT_DIR) / final_filename
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # In MVP local mode, use FFmpeg to create a video from the image and audio
        if Path(avatar_image_path).exists():
            try:
                # Loop image for the duration of the audio
                # Use -t 60 as a safeguard to avoid infinite loops if duration detection fails
                process = subprocess.run([
                    "ffmpeg", "-y", "-loop", "1", "-i", str(avatar_image_path),
                    "-i", str(audio_file_path),
                    "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac", 
                    "-b:a", "192k", "-pix_fmt", "yuv420p", "-shortest",
                    "-t", "60", # Safety limit
                    "-vf", "scale=1280:720", 
                    str(dest_path)
                ], capture_output=True, text=True, timeout=30)
                
                if process.returncode != 0:
                    print(f"ERROR: FFmpeg failed with return code {process.returncode}")
                    print(f"FFmpeg stderr: {process.stderr}")
                    shutil.copy(avatar_image_path, dest_path)
            except Exception as e:
                print(f"ERROR: Exception during FFmpeg execution: {str(e)}")
                shutil.copy(avatar_image_path, dest_path)
        
        update_job_status(job_id, status="completed", progress=100, result_url=f"/api/v1/jobs/{job_id}/download")
        
    except Exception as e:
        update_job_status(job_id, status="failed", error_message=str(e))
        raise
