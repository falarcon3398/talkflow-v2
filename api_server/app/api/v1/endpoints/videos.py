from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
import uuid
import os
from pathlib import Path

from app.database import get_db
from app.models.job import Job
from app.config import settings
from app.workers.celery_app import celery_app
from app.workers.tasks import (
    process_text_to_video_task,
    process_audio_to_video_task,
    process_video_to_video_task
)

router = APIRouter()

@router.post("/text-to-video")
async def create_text_to_video(
    avatar_image: UploadFile = File(...),
    text: str = Form(..., max_length=500),
    voice_id: str = Form(default="voice_en_male_01"),
    output_resolution: str = Form(default="720p"),
    db: Session = Depends(get_db)
):
    # Validate image
    if not avatar_image.content_type.startswith("image/"):
        raise HTTPException(400, "Avatar must be an image file")
    
    job_id = str(uuid.uuid4())
    
    # Save image
    upload_dir = Path(settings.UPLOAD_DIR) / job_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    avatar_path = upload_dir / f"avatar{Path(avatar_image.filename).suffix}"
    
    with avatar_path.open("wb") as f:
        f.write(await avatar_image.read())
        
    # Create job entry
    job = Job(
        id=job_id,
        type="text_to_video",
        status="queued",
        params={
            "text": text,
            "voice_id": voice_id,
            "resolution": output_resolution
        }
    )
    db.add(job)
    db.commit()
    
    # Use delay() which respects task_always_eager
    task = process_text_to_video_task.delay(
        job_id, str(avatar_path), text, voice_id, output_resolution
    )
    
    job.task_id = task.id
    db.commit()
    
    return {"job_id": job_id, "status": "queued"}

@router.post("/audio-to-video")
async def create_audio_to_video(
    avatar_image: UploadFile = File(...),
    audio_file: UploadFile = File(...),
    enhance_quality: bool = Form(default=True),
    db: Session = Depends(get_db)
):
    if not avatar_image.content_type.startswith("image/"):
        raise HTTPException(400, "Avatar must be an image file")
    
    job_id = str(uuid.uuid4())
    
    upload_dir = Path(settings.UPLOAD_DIR) / job_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    avatar_path = upload_dir / f"avatar{Path(avatar_image.filename).suffix}"
    audio_path = upload_dir / f"audio{Path(audio_file.filename).suffix}"
    
    with avatar_path.open("wb") as f:
        f.write(await avatar_image.read())
    with audio_path.open("wb") as f:
        f.write(await audio_file.read())
        
    job = Job(
        id=job_id,
        type="audio_to_video",
        status="queued",
        params={"enhance_quality": enhance_quality}
    )
    db.add(job)
    db.commit()
    
    # Use delay() which respects task_always_eager
    task = process_audio_to_video_task.delay(
        job_id, str(avatar_path), str(audio_path), enhance_quality
    )
    
    job.task_id = task.id
    db.commit()
    
    return {"job_id": job_id, "status": "queued"}
@router.post("/video-to-video")
async def create_video_to_video(
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
    
    # Use delay()
    task = process_video_to_video_task.delay(
        job_id, str(video_path), enhance_quality
    )
    
    job.task_id = task.id
    db.commit()
    
    return {"job_id": job_id, "status": "queued"}
