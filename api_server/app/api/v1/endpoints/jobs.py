from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from pathlib import Path

from app.database import get_db
from app.models.job import Job
from app.config import settings

router = APIRouter()

@router.get("/")
async def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job).order_by(Job.created_at.desc()).all()
    return [{
        "job_id": job.id,
        "status": job.status,
        "progress": job.progress,
        "result_url": job.result_url,
        "error_message": job.error_message,
        "params": job.params,
        "created_at": job.created_at,
        "updated_at": job.updated_at
    } for job in jobs]

@router.get("/{job_id}")
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(404, "Job not found")
    
    return {
        "job_id": job.id,
        "status": job.status,
        "progress": job.progress,
        "result_url": job.result_url,
        "error_message": job.error_message,
        "params": job.params,
        "created_at": job.created_at,
        "updated_at": job.updated_at
    }

@router.get("/{video_id}/download")
async def download_video(video_id: str):
    # For MVP, we look in the local output directory
    video_path = Path(settings.OUTPUT_DIR) / f"{video_id}.mp4"
    
    if not video_path.exists():
        raise HTTPException(404, "Video not found or still processing")
    
    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=f"talkflow_{video_id}.mp4"
    )
