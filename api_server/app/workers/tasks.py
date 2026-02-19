from app.workers.celery_app import celery_app
from app.core.pipeline.orchestrator import run_text_to_video_pipeline, run_audio_to_video_pipeline
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def process_text_to_video_task(self, job_id, avatar_image_path, text, voice_id, resolution):
    logger.info(f"Starting text-to-video task for job {job_id}")
    run_text_to_video_pipeline(job_id, avatar_image_path, text, voice_id, resolution)
    return {"status": "success", "job_id": job_id}

@celery_app.task(bind=True)
def process_audio_to_video_task(self, job_id, avatar_image_path, audio_file_path, enable_enhance):
    logger.info(f"Starting audio-to-video task for job {job_id}")
    run_audio_to_video_pipeline(job_id, avatar_image_path, audio_file_path, enable_enhance)
    return {"status": "success", "job_id": job_id}
@celery_app.task(bind=True)
def process_video_to_video_task(self, job_id, video_path, enhance):
    logger.info(f"Starting video-to-video task for job {job_id}")
    # TODO: Implement video-to-video in orchestrator
    return {"status": "success", "job_id": job_id}
