import uuid
import logging
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.job import Job
from app.models.avatar import Avatar
from app.models.voice import Voice
from app.config import settings
from app.workers.tasks import process_text_to_video_task, process_audio_to_video_task

logger = logging.getLogger(__name__)
router = APIRouter()


def _resolve_avatar_path(avatar: Avatar) -> Path:
    """Resolve the filesystem path of an avatar image."""
    url = avatar.image_url
    if url.startswith("/avatars/") or url.startswith("/static/"):
        return Path(settings.STATIC_DIR) / url.lstrip("/")
    # Custom uploaded avatar: /api/v1/avatars/image/<filename>
    filename = url.split("/")[-1]
    return Path(settings.UPLOAD_DIR) / "avatars" / filename


@router.post("/text-to-video")
async def create_text_to_video(
    avatar_id: str = Form(None),
    text: str = Form(..., max_length=500),
    voice_id: str = Form(default="voice_en_male_01"),
    output_resolution: str = Form(default="720p"),
    aspect_ratio: str = Form(default="16:9"),
    language: str = Form(default="en"),
    db: Session = Depends(get_db)
):
    if not avatar_id:
        raise HTTPException(400, "avatar_id is required")

    avatar = db.query(Avatar).filter(Avatar.id == avatar_id).first()
    if not avatar:
        raise HTTPException(400, f"Avatar {avatar_id} not found")

    avatar_path = _resolve_avatar_path(avatar)
    logger.info(f"Avatar path resolved: {avatar_path} (exists={avatar_path.exists()})")

    # Resolve optional speaker WAV for voice cloning
    speaker_wav_path = None
    
    # Priority 1: Specifically requested voice from library
    if voice_id and voice_id not in ("voice_en_male_01", "voice_en_female_01"):
        library_voice = db.query(Voice).filter(Voice.id == voice_id).first()
        if library_voice:
            fname = library_voice.voice_url.split("/")[-1]
            candidate = Path(settings.UPLOAD_DIR) / "voices" / fname
            if candidate.exists():
                speaker_wav_path = str(candidate)

    # Priority 2: Fallback to Avatar's default voice if no specific voice selected
    if speaker_wav_path is None and avatar.voice_url:
        fname = avatar.voice_url.split("/")[-1]
        candidate = Path(settings.UPLOAD_DIR) / "voices" / fname
        if candidate.exists():
            speaker_wav_path = str(candidate)
            logger.info(f"Using avatar default voice: {speaker_wav_path}")

    # Create job record
    job_id = str(uuid.uuid4())
    job = Job(id=job_id, type="text_to_video", status="queued")
    db.add(job)
    db.commit()

    # Enqueue in Celery (runs on the GPU worker)
    try:
        task = process_text_to_video_task.delay(
            job_id,
            str(avatar_path),
            text,
            voice_id,
            output_resolution,
            speaker_wav_path,
            aspect_ratio,
            language=language
        )
        job.task_id = task.id
        db.commit()
        logger.info(f"Enqueued task {task.id} for job {job_id}")
    except Exception as e:
        logger.error(f"Failed to enqueue Celery task: {e}", exc_info=True)
        job.status = "failed"
        job.error_message = f"Failed to enqueue task: {str(e)}"
        db.commit()
        raise HTTPException(500, f"Could not enqueue task: {str(e)}")

    return {"job_id": job_id, "status": "queued"}


@router.post("/audio-to-video")
async def create_audio_to_video(
    avatar_id: str = Form(None),
    audio_file: UploadFile = File(...),
    enhance_quality: bool = Form(default=True),
    db: Session = Depends(get_db)
):
    if not avatar_id:
        raise HTTPException(400, "avatar_id is required")

    avatar = db.query(Avatar).filter(Avatar.id == avatar_id).first()
    if not avatar:
        raise HTTPException(400, f"Avatar {avatar_id} not found")

    avatar_path = _resolve_avatar_path(avatar)

    job_id = str(uuid.uuid4())
    upload_dir = Path(settings.UPLOAD_DIR) / job_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    audio_path = upload_dir / f"audio{Path(audio_file.filename).suffix}"
    with audio_path.open("wb") as f:
        f.write(await audio_file.read())

    job = Job(id=job_id, type="audio_to_video", status="queued")
    db.add(job)
    db.commit()

    try:
        task = process_audio_to_video_task.delay(
            job_id, str(avatar_path), str(audio_path), enhance_quality
        )
        job.task_id = task.id
        db.commit()
        logger.info(f"Enqueued audio-to-video task {task.id} for job {job_id}")
    except Exception as e:
        logger.error(f"Failed to enqueue audio-to-video task: {e}", exc_info=True)
        job.status = "failed"
        job.error_message = str(e)
        db.commit()
        raise HTTPException(500, str(e))

    return {"job_id": job_id, "status": "queued"}
