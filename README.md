---
title: TalkFlow
emoji: 📽️
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 8000
pinned: false
---

# TalkFlow: Open Source AI Video Avatar Platform

TalkFlow is a SaaS platform that allows businesses to create talking avatar videos from text or audio, using only open-source technologies with commercial-friendly licenses.

## Tech Stack
- **Core**: MuseTalk v1.5, Piper TTS, GFPGAN
- **Backend**: FastAPI, Celery, Redis, PostgreSQL
- **Frontend**: React, Vite, Tailwind CSS v4
- **Infrastructure**: Docker & Docker Compose

## Quick Start

### 1. Prerequisites
- Docker & NVIDIA Container Toolkit (for GPU support)
- 10GB+ Disk Space for models

### 2. Setup Models
Before running, you must download the model weights into the `models/` directory.

- **MuseTalk**: Download from [TencentGameMate/MuseTalk](https://github.com/TencentGameMate/MuseTalk)
- **Piper TTS**: Download ONNX models from [rhasspy/piper](https://github.com/rhasspy/piper)
- **GFPGAN**: Download weights from [TencentARC/GFPGAN](https://github.com/TencentARC/GFPGAN)

### 3. Launch
#### Option A: Docker (Recommended)
```bash
cp .env.example .env
docker compose up --build
```

#### Option B: Local Development (Manual)
**Frontend:**
```bash
cd frontend
npm install
npm run dev
```
**Backend:**
```bash
cd api_server
pip install -r requirements.txt
python3 -m uvicorn app.main:app --reload
```
> [!NOTE]
> Running locally without Docker uses SQLite by default. Lip-sync features require local GPU/CUDA setup.

### 4. Access
- **Web UI**: http://localhost
- **API Docs**: http://localhost/docs
- **Worker Monitor**: http://localhost:5555

## Core Logic Flow
1. **API** receives a Text-to-Video request.
2. **PostgreSQL** records a new job in `queued` status.
3. **Celery** picks up the task.
4. **Worker Pipeline**:
   - `Piper`: Converts text to WAV audio.
   - `MuseTalk`: Syncs avatar facial features to the audio.
   - `GFPGAN`: Enhances facial quality and upscales the video.
5. **Job Status** is updated to `completed`.
6. **Frontend** polls status and provides a download link.
