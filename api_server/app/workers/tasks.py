from app.workers.celery_app import celery_app
from app.core.pipeline.orchestrator import run_text_to_video_pipeline, run_audio_to_video_pipeline
import logging

logger = logging.getLogger(__name__)

def run_text_to_video_task(job_id, avatar_image_path, text, voice_id, resolution, speaker_wav_path=None):
    print(f"\n[BACKGROUND] Starting text-to-video for job {job_id}")
    logger.info(f"Starting text-to-video task for job {job_id}")
    try:
        run_text_to_video_pipeline(job_id, avatar_image_path, text, voice_id, resolution, speaker_wav_path)
        print(f"[BACKGROUND] Completed job {job_id}")
    except Exception as e:
        print(f"[BACKGROUND] FAILED job {job_id}: {str(e)}")
        logger.error(f"Task failed: {str(e)}")

def run_audio_to_video_task(job_id, avatar_image_path, audio_file_path, enable_enhance):
    print(f"\n[BACKGROUND] Starting audio-to-video for job {job_id}")
    logger.info(f"Starting audio-to-video task for job {job_id}")
    try:
        run_audio_to_video_pipeline(job_id, avatar_image_path, audio_file_path, enable_enhance)
        print(f"[BACKGROUND] Completed job {job_id}")
    except Exception as e:
        print(f"[BACKGROUND] FAILED job {job_id}: {str(e)}")
        logger.error(f"Task failed: {str(e)}")

@celery_app.task(bind=True)
def process_text_to_video_task(self, job_id, avatar_image_path, text, voice_id, resolution, speaker_wav_path=None):
    run_text_to_video_task(job_id, avatar_image_path, text, voice_id, resolution, speaker_wav_path)
    return {"status": "success", "job_id": job_id}

@celery_app.task(bind=True)
def process_audio_to_video_task(self, job_id, avatar_image_path, audio_file_path, enable_enhance):
    run_audio_to_video_task(job_id, avatar_image_path, audio_file_path, enable_enhance)
    return {"status": "success", "job_id": job_id}

@celery_app.task(bind=True)
def process_video_to_video_task(self, job_id, video_path, enhance):
    print(f"\n[BACKGROUND] Starting video-to-video task for job {job_id}")
    logger.info(f"Starting video-to-video task for job {job_id}")
    # TODO: Implement video-to-video in orchestrator
    return {"status": "success", "job_id": job_id}
