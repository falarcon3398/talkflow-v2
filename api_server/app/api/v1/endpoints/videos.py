from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
import uuid
import os
from pathlib import Path

from app.database import get_db
from app.models.job import Job
from app.config import settings
from app.models.avatar import Avatar
from app.models.voice import Voice
from app.workers.celery_app import celery_app
from app.workers.tasks import (
    run_text_to_video_task,
    run_audio_to_video_task,
    process_video_to_video_task
)

router = APIRouter()

@router.post("/text-to-video")
async def create_text_to_video(
    background_tasks: BackgroundTasks,
    avatar_image: UploadFile = File(None),
    avatar_id: str = Form(None),
    text: str = Form(..., max_length=500),
    voice_id: str = Form(default="voice_en_male_01"),
    output_resolution: str = Form(default="720p"),
    aspect_ratio: str = Form(default="16:9"),
    db: Session = Depends(get_db)
):
    # Determine the avatar image path
    job_id = str(uuid.uuid4())
    upload_dir = Path(settings.UPLOAD_DIR) / job_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    avatar_path = None

    if avatar_id:
        # Fetch from DB
        avatar = db.query(Avatar).filter(Avatar.id == avatar_id).first()
        if avatar:
            # If it's a preset, it might point to /avatars/...
            if avatar.image_url.startswith("/avatars/"):
                # Use absolute path relative to this file
                # app/api/v1/endpoints/videos.py -> 3 levels up -> app/static
                avatar_path = Path(settings.STATIC_DIR) / avatar.image_url.lstrip("/")
            else:
                # Custom avatar, image_url is "/api/v1/avatars/image/ID.ext"
                # Parse ID/filename from URL
                filename = avatar.image_url.split("/")[-1]
                avatar_path = Path(settings.UPLOAD_DIR) / "avatars" / filename
        
    if not avatar_path and avatar_image:
        # Fallback to uploaded image
        if not avatar_image.content_type.startswith("image/"):
            raise HTTPException(400, "Avatar must be an image file")
            
        avatar_path = upload_dir / f"avatar{Path(avatar_image.filename).suffix}"
        with avatar_path.open("wb") as f:
            f.write(await avatar_image.read())

    if not avatar_path or not avatar_path.exists():
        raise HTTPException(400, "No valid avatar image found")
        
    # Determine if we have a cloned voice
    speaker_wav_path = None
    
    # Check if a custom voice_id was passed
    if voice_id and voice_id != "voice_en_male_01":
        # Check in Voice Library first
        library_voice = db.query(Voice).filter(Voice.id == voice_id).first()
        if library_voice:
            filename = library_voice.voice_url.split("/")[-1]
            speaker_wav_path = Path(settings.UPLOAD_DIR) / "voices" / filename
        else:
            # Fallback to Avatar-linked voice
            voice_avatar = db.query(Avatar).filter(Avatar.id == voice_id).first()
            if voice_avatar and voice_avatar.voice_url:
                filename = voice_avatar.voice_url.split("/")[-1]
                speaker_wav_path = Path(settings.UPLOAD_DIR) / "voices" / filename
        
        if speaker_wav_path and not speaker_wav_path.exists():
            speaker_wav_path = None

    # Fallback to the avatar's own voice
    if not speaker_wav_path and avatar_id:
        avatar = db.query(Avatar).filter(Avatar.id == avatar_id).first()
        if avatar and avatar.voice_url:
            filename = avatar.voice_url.split("/")[-1]
            speaker_wav_path = Path(settings.UPLOAD_DIR) / "voices" / filename
            if not speaker_wav_path.exists():
                speaker_wav_path = None

    # Validate aspect_ratio
    if aspect_ratio not in ("16:9", "9:16"):
        aspect_ratio = "16:9"

    # Create job entry
    job = Job(
        id=job_id,
        type="text_to_video",
        status="queued",
        params={
            "text": text,
            "voice_id": voice_id,
            "resolution": output_resolution,
            "aspect_ratio": aspect_ratio,
            "avatar_id": avatar_id,
            "avatar_path": str(avatar_path.resolve()),
            "speaker_wav_path": str(speaker_wav_path.resolve()) if speaker_wav_path else None
        }
    )
    db.add(job)
    db.commit()
    
    # Use BackgroundTasks instead of Celery delay() to avoid blocking
    background_tasks.add_task(
        run_text_to_video_task,
        job_id, str(avatar_path.resolve()), text, voice_id, output_resolution,
        str(speaker_wav_path.resolve()) if speaker_wav_path else None,
        aspect_ratio
    )
    
    job.task_id = job_id
    db.commit()
    
    return {"job_id": job_id, "status": "queued"}

@router.post("/audio-to-video")
async def create_audio_to_video(
    background_tasks: BackgroundTasks,
    avatar_image: UploadFile = File(None),
    avatar_id: str = Form(None),
    audio_file: UploadFile = File(...),
    enhance_quality: bool = Form(default=True),
    db: Session = Depends(get_db)
):
    job_id = str(uuid.uuid4())
    upload_dir = Path(settings.UPLOAD_DIR) / job_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    avatar_path = None
    if avatar_id:
        avatar = db.query(Avatar).filter(Avatar.id == avatar_id).first()
        if avatar:
            if avatar.image_url.startswith("/avatars/"):
                avatar_path = Path(settings.STATIC_DIR) / avatar.image_url.lstrip("/")
            else:
                filename = avatar.image_url.split("/")[-1]
                avatar_path = Path(settings.UPLOAD_DIR) / "avatars" / filename

    if not avatar_path and avatar_image:
        if not avatar_image.content_type.startswith("image/"):
            raise HTTPException(400, "Avatar must be an image file")
        avatar_path = upload_dir / f"avatar{Path(avatar_image.filename).suffix}"
        with avatar_path.open("wb") as f:
            f.write(await avatar_image.read())

    if not avatar_path or not avatar_path.exists():
        raise HTTPException(400, "No valid avatar image found")

    audio_path = upload_dir / f"audio{Path(audio_file.filename).suffix}"
    with audio_path.open("wb") as f:
        f.write(await audio_file.read())
        
    job = Job(
        id=job_id,
        type="audio_to_video",
        status="queued",
        params={
            "enhance_quality": enhance_quality,
            "avatar_id": avatar_id,
            "avatar_path": str(avatar_path.resolve()),
            "audio_path": str(audio_path.resolve())
        }
    )
    db.add(job)
    db.commit()
    
    # Use BackgroundTasks instead of Celery delay()
    background_tasks.add_task(
        run_audio_to_video_task,
        job_id, str(avatar_path.resolve()), str(audio_path.resolve()), enhance_quality
    )
    
    job.task_id = job_id
    db.commit()
    
    return {"job_id": job_id, "status": "queued"}
@router.post("/video-to-video")
async def create_video_to_video(
    background_tasks: BackgroundTasks,
    reference_video: UploadFile = File(...),
    enhance_quality: bool = Form(default=True),
    db: Session = Depends(get_db)
):
    # This involves extracting frames/motion from a reference video
    job_id = str(uuid.uuid4())
    
    upload_dir = Path(settings.UPLOAD_DIR) / job_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    video_path = upload_dir / f"reference{Path(reference_video.filename).suffix}"
    
    with video_path.open("wb") as f:
        f.write(await reference_video.read())
        
    job = Job(
        id=job_id,
        type="video_to_video",
        status="queued",
        params={"enhance_quality": enhance_quality}
    )
    db.add(job)
    db.commit()
    
    # Use BackgroundTasks
    background_tasks.add_task(
        process_video_to_video_task,
        None, job_id, str(video_path), enhance_quality
    )
    
    job.task_id = job_id
    db.commit()
    
    return {"job_id": job_id, "status": "queued"}
