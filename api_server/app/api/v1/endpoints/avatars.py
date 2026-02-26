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
    voice_clip: UploadFile = File(None),
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

    # Save voice clip if provided
    voice_url = None
    if voice_clip:
        voice_dir = Path(settings.UPLOAD_DIR) / "voices"
        voice_dir.mkdir(parents=True, exist_ok=True)
        voice_filename = f"{avatar_id}{Path(voice_clip.filename).suffix}"
        voice_path = voice_dir / voice_filename
        with voice_path.open("wb") as f:
            f.write(await voice_clip.read())
        voice_url = f"/api/v1/avatars/voice/{voice_filename}"

    avatar = Avatar(
        id=avatar_id,
        name=name,
        type=type,
        image_url=image_url,
        voice_url=voice_url
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

@router.get("/voice/{voice_name}")
async def get_avatar_voice(voice_name: str):
    from fastapi.responses import FileResponse
    voice_path = Path(settings.UPLOAD_DIR) / "voices" / voice_name
    if not voice_path.exists():
        raise HTTPException(404, "Voice clip not found")
    return FileResponse(voice_path)

@router.put("/{avatar_id}")
async def update_avatar(
    avatar_id: str,
    name: str = Form(...),
    db: Session = Depends(get_db)
):
    avatar = db.query(Avatar).filter(Avatar.id == avatar_id).first()
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")
    
    avatar.name = name
    db.commit()
    db.refresh(avatar)
    return avatar

@router.delete("/{avatar_id}")
async def delete_avatar(
    avatar_id: str,
    db: Session = Depends(get_db)
):
    avatar = db.query(Avatar).filter(Avatar.id == avatar_id).first()
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")
    
    # Delete image file if it's a custom upload
    if "/api/v1/avatars/image/" in avatar.image_url:
        filename = avatar.image_url.split("/")[-1]
        image_path = Path(settings.UPLOAD_DIR) / "avatars" / filename
        if image_path.exists():
            try:
                os.remove(image_path)
            except Exception as e:
                print(f"Error deleting image file: {e}")

    # Delete voice file if it exists
    if avatar.voice_url and "/api/v1/avatars/voice/" in avatar.voice_url:
        filename = avatar.voice_url.split("/")[-1]
        voice_path = Path(settings.UPLOAD_DIR) / "voices" / filename
        if voice_path.exists():
            try:
                os.remove(voice_path)
            except Exception as e:
                print(f"Error deleting voice file: {e}")

    db.delete(avatar)
    db.commit()
    return {"message": "Avatar deleted successfully"}
