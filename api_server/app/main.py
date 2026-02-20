from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import videos, jobs, avatars
from app.database import Base, engine
from fastapi.staticfiles import StaticFiles
from app.config import settings
from pathlib import Path

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TalkFlow API",
    version="1.0.0",
    description="Open Source Avatar Video Generation Platform"
)

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

# Required for Vercel
handler = app
