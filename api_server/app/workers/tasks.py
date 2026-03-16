import logging
from app.workers.celery_app import celery_app
from app.core.pipeline.orchestrator import run_text_to_video_pipeline, run_audio_to_video_pipeline

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.workers.tasks.process_text_to_video_task", max_retries=0)
def process_text_to_video_task(self, job_id, avatar_image_path, text, voice_id, resolution, speaker_wav_path=None, aspect_ratio="16:9", language="en"):
    logger.info(f"[WORKER] Starting text-to-video for job {job_id} (Language: {language})")
    try:
        run_text_to_video_pipeline(job_id, avatar_image_path, text, voice_id, resolution, speaker_wav_path, aspect_ratio, language=language)
        logger.info(f"[WORKER] Completed job {job_id}")
        return {"status": "success", "job_id": job_id}
    except Exception as e:
        logger.error(f"[WORKER] FAILED job {job_id}: {str(e)}", exc_info=True)
        raise


@celery_app.task(bind=True, name="app.workers.tasks.process_audio_to_video_task", max_retries=0)
def process_audio_to_video_task(self, job_id, avatar_image_path, audio_file_path, enable_enhance):
    logger.info(f"[WORKER] Starting audio-to-video for job {job_id}")
    try:
        run_audio_to_video_pipeline(job_id, avatar_image_path, audio_file_path, enable_enhance)
        logger.info(f"[WORKER] Completed job {job_id}")
        return {"status": "success", "job_id": job_id}
    except Exception as e:
        logger.error(f"[WORKER] FAILED job {job_id}: {str(e)}", exc_info=True)
        raise


@celery_app.task(bind=True, name="app.workers.tasks.process_video_to_video_task", max_retries=0)
def process_video_to_video_task(self, job_id, video_path, enhance):
    logger.info(f"[WORKER] Video-to-video task for job {job_id} not yet implemented")
    return {"status": "success", "job_id": job_id}


# Backward-compatible wrappers (required by main.py startup)
def run_text_to_video_task(job_id, avatar_image_path, text, voice_id, resolution, speaker_wav_path=None, aspect_ratio="16:9", language="en"):
    run_text_to_video_pipeline(job_id, avatar_image_path, text, voice_id, resolution, speaker_wav_path, aspect_ratio, language=language)


def run_audio_to_video_task(job_id, avatar_image_path, audio_file_path, enable_enhance):
    run_audio_to_video_pipeline(job_id, avatar_image_path, audio_file_path, enable_enhance)
