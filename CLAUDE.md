# CLAUDE.md — TalkFlow Video Avatar

## Project Overview

TalkFlow Video Avatar is a full-stack GPU-powered application for generating avatar videos with real-time lipsync. It supports text-to-video, audio-to-video, and live WebRTC conversations with AI avatars using MuseTalk inference.

**Production server:** `videoavatar.ibl.ai` (AWS EC2 GPU instance, Ubuntu 22.04)

## Quick Reference

```bash
# Local development
docker compose build && docker compose up -d

# Check status
docker compose ps && docker ps && nvidia-smi

# Logs
docker logs -f talkflow-backend
docker logs -f talkflow-worker
docker compose logs -f

# SSH to server
ssh -i ~/.ssh/ibl-admin-gpu.pem ubuntu@videoavatar.ibl.ai
```

## Architecture

```
Browser → Nginx (:80)
             ├── Frontend (React/Vite → static via nginx)
             ├── /api/* → Backend (FastAPI :8000)
             └── /ws/*  → Backend (WebRTC/WebSocket)
                            ├── Redis (broker)
                            ├── PostgreSQL (database)
                            ├── MinIO (object storage)
                            └── Celery Worker (GPU)
                                 └── MuseTalk / SadTalker
```

## Repository Structure

```
api_server/
  app/
    main.py              # FastAPI app, router registration, startup hooks
    config.py            # Pydantic settings (Docker/Vercel/local)
    database.py          # SQLAlchemy Base + engine
    api/v1/endpoints/
      videos.py          # POST /text-to-video, /audio-to-video
      jobs.py            # Job CRUD, download, batch ops
      avatars.py         # Avatar CRUD
      voices.py          # Voice library
    models/
      job.py             # Job entity (status, progress, result_url)
      avatar.py          # Avatar entity
      voice.py           # Voice entity
    core/
      pipeline/
        orchestrator.py  # Coordinates TTS → lipsync → enhance → output
        tts.py           # ElevenLabs API + XTTS voice cloning
        lipsync.py       # Dispatches to MuseTalk or SadTalker
        enhance.py       # Video quality enhancement
      pipeline_adapters/
        musetalk_adapter.py  # MuseTalk subprocess inference
        sadtalker_adapter.py # SadTalker fallback
      storage/
        minio_client.py  # S3-compatible storage
    workers/
      celery_app.py      # Celery config (Redis broker)
      tasks.py           # process_text_to_video_task, process_audio_to_video_task
    live_call/
      router.py          # Avatar upload, selection, idle video
      webrtc.py          # LiveCallPeer: RTCPeerConnection, VAD, tracks
      tracks.py          # ClipVideoTrack (idle/talking), QueuedAudioTrack
      vad.py             # Voice Activity Detection (webrtcvad)
      agent.py           # VoiceAgent (OpenAI LLM conversation)
      workers.py         # Real-time MuseTalk/Wav2Lip lipsync
      storage.py         # Avatar file management
      settings.py        # LiveCall config (API keys, model paths)
  musetalk/              # MuseTalk model code (inference, utils, whisper)
    scripts/inference.py # Entry point for lipsync inference
    configs/inference/   # Per-job YAML task configs

frontend/
  src/
    App.jsx              # Main app (sidebar nav: library, generate, scripts)
    api/client.js        # avatarApi, videoApi, voiceApi
    components/ui/       # Button, Card, Input, Modal, Badge
    theme/tokens.js      # Design tokens (colors, gradients, typography)
    views/UIPreview.jsx  # Living style guide

nginx/nginx.conf         # Reverse proxy config
scripts/                 # Deployment, model download, inference utils
configs/                 # MuseTalk inference YAML configs
docker-compose.yml       # Full stack orchestration
Dockerfile               # CUDA 11.8 + Python 3.10 + system deps
```

## Key Data Flows

### Text-to-Video Pipeline
1. `POST /api/v1/videos/text-to-video` → creates Job in DB
2. Enqueues `process_text_to_video_task` via Celery
3. Worker executes: TTS → MuseTalk lipsync → enhance → ffmpeg aspect ratio
4. Output saved to `/app/data/outputs/{job_id}/`
5. Frontend polls `/api/v1/jobs/{job_id}`, downloads result

### Live Call (WebRTC)
1. Upload avatar → build idle video (SadTalker)
2. WebSocket `/ws/realtime?avatar_id=...` → RTCPeerConnection
3. User audio → VAD segmentation → VoiceAgent → TTS response
4. Real-time MuseTalk lipsync → video/audio tracks to browser

## Critical Behaviors

- **Lipsync lock:** Sequential GPU execution (thread lock) prevents memory thrashing
- **Celery pool:** Solo pool (single process) — no multiprocessing for GPU safety
- **Static fallback:** If MuseTalk fails, pipeline returns static image — this means the issue is NOT fixed
- **Job recovery:** Startup hook re-queues stuck jobs (queued/processing state)
- **Aspect ratio:** Applied post-generation via ffmpeg (9:16 for mobile, 16:9 default)

## Environment Variables

Required in `.env`:
```
POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
DATABASE_URL=postgresql://talkflow:changeme@postgres:5432/talkflow
REDIS_URL=redis://redis:6379/0
MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY
MODELS_PATH=/app/models
UPLOAD_DIR=/app/data/uploads
PROCESSING_DIR=/app/data/processing
OUTPUT_DIR=/app/data/outputs
```

Optional for live call:
```
OPENAI_API_KEY, ELEVENLABS_API_KEY
LIPSYNC_ENGINE=musetalk  (or sadtalker)
```

## Server Deployment Rules

1. **Persistent fixes only** — never edit inside running containers. Fixes go in: Git repo, Docker image, or mounted volumes.
2. **Persistent paths on server:**
   - `/opt/talkflow/models` → mounted to `/app/models`
   - `/opt/talkflow/data/{uploads,processing,outputs}` → mounted to `/app/data/`
3. **After reboot:** Stack auto-starts via systemd (`talkflow-compose.service`). Do NOT rebuild — images are cached.
4. **Success = real video** — never claim fixed unless MuseTalk produces actual lipsync video (not static fallback).
5. **Verify flow:** `docker compose ps` → `nvidia-smi` → check worker/backend logs → verify output files.

## GPU Requirements

- NVIDIA GPU with 16GB+ VRAM (A10G on g5.xlarge)
- NVIDIA Container Toolkit installed on host
- Verify: `nvidia-smi` on host AND `docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi`

## Common Failure Modes

| Issue | Symptom | Fix |
|-------|---------|-----|
| Dependency mismatch | `ImportError: cached_download` | Pin `huggingface_hub` version |
| Missing models | MuseTalk path errors | Check `/opt/talkflow/models/` mounts |
| Wrong model path | Files exist but code can't find them | Check relative vs absolute paths |
| Output discovery | MuseTalk succeeds but "no MP4 found" | Check output path in worker matches mount |
| Non-persistent fix | Works until reboot | Fix must be in repo/image/volume |
| WebSocket failure | Live call won't connect | Check nginx upgrade/connection headers |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19 + Vite + Tailwind CSS 4 |
| Backend | FastAPI + Python 3.10 + Uvicorn |
| Worker | Celery + Redis (solo pool) |
| Database | PostgreSQL 15 |
| Storage | MinIO (S3-compatible) |
| Inference | MuseTalk (lipsync) + XTTS v2 (voice clone) |
| Real-time | WebRTC (aiortc) + WebSockets |
| Proxy | Nginx |
| GPU | CUDA 11.8 + cuDNN 8 |

## Testing

Minimal test suite — primarily integration tested on deployment:
- `api_server/test_aiortc.py` — WebRTC validation
- `api_server/scripts/test_musetalk_env.py` — MuseTalk environment check
- `api_server/musetalk/test_ffmpeg.py` — FFmpeg validation

## Style & Conventions

- Backend: Python 3.10, FastAPI with Pydantic models, SQLAlchemy ORM
- Frontend: React JSX, Tailwind utility classes, glassmorphism design system
- Linting: ruff + black (backend), prettier + eslint (frontend)
- No formal test suite — validate by running the pipeline end-to-end
- Commit messages: conventional style (`feat:`, `fix:`, `docs:`)
