from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from pathlib import Path
import os

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
        "title": job.title,
        "project_id": job.project_id,
        "created_at": job.created_at,
        "updated_at": job.updated_at
    } for job in jobs]

@router.patch("/{job_id}")
async def update_job(job_id: str, data: dict, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(404, "Job not found")
    
    if "title" in data:
        job.title = data["title"]
    if "project_id" in data:
        job.project_id = data["project_id"]
        
    db.commit()
    return {
        "job_id": job.id,
        "title": job.title,
        "project_id": job.project_id
    }

@router.get("/{job_id}/download")
async def download_video(job_id: str):
    video_path = Path(settings.OUTPUT_DIR).resolve() / f"{job_id}.mp4"
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Checking for video at: {video_path}")
    
    if not video_path.exists():
        logger.warning(f"Video NOT FOUND at: {video_path}")
        raise HTTPException(404, f"Video not found or still processing. Path checked: {video_path}")
    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=f"talkflow_{job_id}.mp4"
    )

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

@router.delete("/{job_id}")
async def delete_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(404, "Job not found")

    # Delete output video file if it exists
    video_path = Path(settings.OUTPUT_DIR) / f"{job_id}.mp4"
    if video_path.exists():
        try:
            os.remove(video_path)
        except Exception:
            pass  # best-effort

    db.delete(job)
    db.commit()
    return {"deleted": True, "job_id": job_id}

@router.post("/batch-delete")
async def batch_delete_jobs(job_ids: list[str], db: Session = Depends(get_db)):
    deleted_ids = []
    for job_id in job_ids:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            # Delete output video file if it exists
            video_path = Path(settings.OUTPUT_DIR) / f"{job_id}.mp4"
            if video_path.exists():
                try:
                    os.remove(video_path)
                except Exception:
                    pass
            db.delete(job)
            deleted_ids.append(job_id)
    
    db.commit()
    return {"deleted_count": len(deleted_ids), "deleted_ids": deleted_ids}

@router.patch("/batch-update")
async def batch_update_jobs(update_data: dict, db: Session = Depends(get_db)):
    job_ids = update_data.get("job_ids", [])
    data = update_data.get("data", {})
    
    updated_ids = []
    for job_id in job_ids:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            if "title" in data:
                job.title = data["title"]
            if "project_id" in data:
                job.project_id = data["project_id"]
            updated_ids.append(job_id)
            
    db.commit()
    return {"updated_count": len(updated_ids), "updated_ids": updated_ids}
