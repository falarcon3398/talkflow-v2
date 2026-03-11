from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import videos, jobs, avatars, voices
from app.database import Base, engine
from fastapi.staticfiles import StaticFiles
from app.config import settings
from pathlib import Path

# Create tables
Base.metadata.create_all(bind=engine)

def start_stuck_jobs():
    from app.database import SessionLocal
    from app.models.job import Job
    from app.models.avatar import Avatar
    from app.workers.tasks import process_text_to_video_task, process_audio_to_video_task
    from app.config import settings
    from pathlib import Path
    import threading
    import time

    def worker():
        # Wait a bit for the server to be fully ready
        time.sleep(5)
        db = SessionLocal()
        try:
            # Re-queue jobs that are stuck in queued or processing
            stuck_jobs = db.query(Job).filter(Job.status.in_(["queued", "processing"])).all()
            if stuck_jobs:
                print(f"\n[STARTUP] Found {len(stuck_jobs)} stuck jobs. Re-queuing...")
                for job in stuck_jobs:
                    params = job.params or {}
                    job_id = job.id
                    
                    # Try to resolve avatar_path if missing
                    avatar_path = params.get("avatar_path")
                    if not avatar_path:
                        avatar_id = params.get("avatar_id")
                        if avatar_id:
                            avatar = db.query(Avatar).filter(Avatar.id == avatar_id).first()
                            if avatar:
                                if avatar.image_url.startswith("/avatars/"):
                                    avatar_path = str(Path(settings.STATIC_DIR) / avatar.image_url.lstrip("/"))
                                else:
                                    filename = avatar.image_url.split("/")[-1]
                                    avatar_path = str(Path(settings.UPLOAD_DIR) / "avatars" / filename)
                    
                    if not avatar_path:
                        print(f"[STARTUP] Skipping job {job_id}: Could not resolve avatar_path")
                        continue

                    if job.type == "text_to_video":
                        print(f"[STARTUP] Re-triggering text-to-video for {job_id}")
                        process_text_to_video_task.delay(job_id, avatar_path, params.get("text"), params.get("voice_id"), params.get("resolution"))
                    elif job.type == "audio_to_video":
                        audio_path = params.get("audio_path")
                        if not audio_path:
                            audio_path = str(Path(settings.UPLOAD_DIR) / job_id / "audio.wav")
                        
                        print(f"[STARTUP] Re-triggering audio-to-video for {job_id}")
                        process_audio_to_video_task.delay(job_id, avatar_path, audio_path, params.get("enhance_quality"))
        except Exception as e:
            print(f"[STARTUP] Recovery failed: {e}")
        finally:
            db.close()

    # Start recovery in a separate thread to not block FastAPI startup
    threading.Thread(target=worker, daemon=True).start()

app = FastAPI(
    title="TalkFlow API",
    version="1.0.0",
    description="Open Source Avatar Video Generation Platform"
)

@app.on_event("startup")
async def on_startup():
    start_stuck_jobs()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static Files
static_avatars_path = Path(settings.STATIC_DIR)
if static_avatars_path.exists():
    app.mount("/avatars", StaticFiles(directory=str(static_avatars_path / "avatars")), name="avatars")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "database": "connected",
            "redis": "connected"
        }
    }

# Include routers
app.include_router(videos.router, prefix="/api/v1/videos", tags=["videos"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["jobs"])
app.include_router(avatars.router, prefix="/api/v1/avatars", tags=["avatars"])
app.include_router(voices.router, prefix="/api/v1/voices", tags=["voices"])

# ------------------- LIVE CALL integration -------------------
try:
    from app.live_call import router as live_router
    from app.live_call.settings import ensure_external_dirs
    
    # Ensure directories on external storage exist
    ensure_external_dirs()
    
    # Include the live call router (WebRTC signaling + avatar management)
    app.include_router(live_router)
    
    # Mount /live static UI (served by backend)
    live_static_dir = Path(__file__).resolve().parent / "static" / "live"
    if live_static_dir.exists():
        app.mount("/live", StaticFiles(directory=str(live_static_dir), html=True), name="live")
        print(f"[LIVE CALL] Static UI mounted at /live from {live_static_dir}")
    else:
        print(f"[LIVE CALL] Warning: Static UI directory not found at {live_static_dir}")
        
except Exception as e:
    print(f"[LIVE CALL] Initialization failed: {e}")
# ----------------- END LIVE CALL integration -----------------

# Required for Vercel
handler = app

