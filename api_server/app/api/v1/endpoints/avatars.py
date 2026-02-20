from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
import uuid
import os
from pathlib import Path

from app.database import get_db
from app.models.avatar import Avatar
from app.config import settings

router = APIRouter()

@router.get("/")
async def list_avatars(db: Session = Depends(get_db)):
    avatars = db.query(Avatar).all()
    # Add default avatars if none exist (for the first time)
    if not avatars:
        defaults = [
            {"id": "1", "name": "Shakespeare", "type": "Historic", "image_url": "/avatars/shakespeare.jpg"},
            {"id": "2", "name": "Thomas Aquinas", "type": "Historic", "image_url": "/avatars/monk.jpg"},
            {"id": "3", "name": "Marcus Aurelius", "type": "Historic", "image_url": "/avatars/marcus_aurelius.jpg"},
            {"id": "4", "name": "Tech CEO", "type": "Modern", "image_url": "/avatars/modern_male.png"}
        ]
        for d in defaults:
            avatar = Avatar(**d)
            db.add(avatar)
        db.commit()
        avatars = db.query(Avatar).all()
    
    return avatars

@router.post("/")
async def create_avatar(
    name: str = Form(...),
    type: str = Form(default="Custom"),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    avatar_id = str(uuid.uuid4())
    
    # Save image physically
    upload_dir = Path(settings.UPLOAD_DIR) / "avatars"
    upload_dir.mkdir(parents=True, exist_ok=True)
    image_path = upload_dir / f"{avatar_id}{Path(image.filename).suffix}"
    
    with image_path.open("wb") as f:
        f.write(await image.read())
    
    # We'll use a local path that Nginx or FastAPI can serve
    # In a real environment this would be the MinIO/S3 URL
    image_url = f"/api/v1/avatars/image/{avatar_id}{Path(image.filename).suffix}"

    avatar = Avatar(
        id=avatar_id,
        name=name,
        type=type,
        image_url=image_url
    )
    db.add(avatar)
    db.commit()
    db.refresh(avatar)
    
    return avatar

@router.get("/image/{image_name}")
async def get_avatar_image(image_name: str):
    from fastapi.responses import FileResponse
    image_path = Path(settings.UPLOAD_DIR) / "avatars" / image_name
    if not image_path.exists():
        raise HTTPException(404, "Image not found")
    return FileResponse(image_path)
