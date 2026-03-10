from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
import uuid
import os
from pathlib import Path
from datetime import datetime

from app.database import get_db
from app.models.voice import Voice
from app.config import settings

router = APIRouter()

@router.get("/")
async def list_voices(db: Session = Depends(get_db)):
    return db.query(Voice).order_by(Voice.created_at.desc()).all()

@router.post("/")
async def upload_voice(
    name: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    voice_id = str(uuid.uuid4())
    
    # Save file
    voice_dir = Path(settings.UPLOAD_DIR) / "voices"
    voice_dir.mkdir(parents=True, exist_ok=True)
    
    extension = Path(file.filename).suffix
    if extension.lower() not in [".wav", ".mp3", ".m4a"]:
        raise HTTPException(400, "Only audio files (wav, mp3, m4a) are supported")
        
    filename = f"{voice_id}{extension}"
    voice_path = voice_dir / filename
    
    with voice_path.open("wb") as f:
        f.write(await file.read())
        
    voice_url = f"/api/v1/voices/file/{filename}"
    
    voice = Voice(
        id=voice_id,
        name=name,
        voice_url=voice_url
    )
    db.add(voice)
    db.commit()
    db.refresh(voice)
    
    return voice

@router.get("/file/{filename}")
async def get_voice_file(filename: str):
    from fastapi.responses import FileResponse
    voice_path = Path(settings.UPLOAD_DIR) / "voices" / filename
    if not voice_path.exists():
        raise HTTPException(404, "Voice file not found")
    return FileResponse(voice_path)

@router.patch("/{voice_id}")
async def rename_voice(
    voice_id: str,
    name: str = Form(None),
    db: Session = Depends(get_db)
):
    voice = db.query(Voice).filter(Voice.id == voice_id).first()
    if not voice:
        raise HTTPException(404, "Voice not found")
    
    if name:
        voice.name = name
        
    db.commit()
    db.refresh(voice)
    return voice

@router.delete("/{voice_id}")
async def delete_voice(
    voice_id: str,
    db: Session = Depends(get_db)
):
    voice = db.query(Voice).filter(Voice.id == voice_id).first()
    if not voice:
        raise HTTPException(404, "Voice not found")
        
    # Delete physical file
    filename = voice.voice_url.split("/")[-1]
    voice_path = Path(settings.UPLOAD_DIR) / "voices" / filename
    if voice_path.exists():
        try:
            os.remove(voice_path)
        except Exception as e:
            print(f"Error deleting voice file: {e}")
            
    db.delete(voice)
    db.commit()
    return {"message": "Voice deleted successfully"}
