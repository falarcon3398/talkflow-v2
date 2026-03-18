# TalkFlow Video Avatar

TalkFlow Video Avatar is a full-stack application for generating avatar-based videos from text, audio, and source media. It includes a frontend UI, backend API, Celery worker pipeline, Redis, PostgreSQL, MinIO, Nginx, and GPU-based MuseTalk inference for lipsync and avatar video generation.

## Overview

This project supports:
- Text-to-video avatar generation
- Audio-to-video avatar generation
- Video-to-video avatar workflows
- MuseTalk-powered lipsync
- Background processing with Celery
- Persistent asset storage
- Frontend + backend routing through Nginx
- GPU inference on AWS EC2

## Recommended Deployment

This project is intended to run on a server-based Docker deployment.

Recommended environment:
- AWS EC2 g5.xlarge or similar GPU instance
- Ubuntu 22.04
- Docker + Docker Compose
- NVIDIA Container Toolkit
- Persistent storage for models and generated files

Important:
The server is the source of truth. Do not rely on temporary fixes inside running containers. Permanent fixes must live in:
- the Git repo
- the Docker image
- mounted persistent volumes
- server-level configuration

## Architecture

Browser
  |
Nginx
  |-- Frontend
  |-- Backend API
         |
       Redis
         |
      Celery Worker
         |
      MuseTalk / GPU
         |
 Processing + Output Files
         |
   Generated Avatar Videos

## Repository Structure

.
├── api_server/
├── frontend/
├── models/
├── nginx/
├── scripts/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md

## Main Services

### Frontend
User-facing web application.

### Backend API
Handles application logic, job creation, orchestration, and endpoints.

### Worker
Celery worker that processes generation jobs and runs MuseTalk inference.

### Redis
Queue broker and runtime coordination.

### PostgreSQL
Primary relational database.

### MinIO
Object storage for assets and related files.

### Nginx
Reverse proxy for frontend and backend traffic.

### Models
MuseTalk checkpoints and related inference files.

## Recommended Persistent Server Paths

Use persistent directories on the server so models and generated files survive restarts and rebuilds.

/opt/talkflow/models
/opt/talkflow/data/uploads
/opt/talkflow/data/processing
/opt/talkflow/data/outputs

Create them with:

sudo mkdir -p /opt/talkflow/models
sudo mkdir -p /opt/talkflow/data/uploads
sudo mkdir -p /opt/talkflow/data/processing
sudo mkdir -p /opt/talkflow/data/outputs
sudo chown -R $USER:$USER /opt/talkflow

## Environment Variables

Create a .env file in the project root.

POSTGRES_USER=talkflow
POSTGRES_PASSWORD=changeme
POSTGRES_DB=talkflow

MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin

DATABASE_URL=postgresql://talkflow:changeme@postgres:5432/talkflow
REDIS_URL=redis://redis:6379/0

MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

MODELS_PATH=/app/models
UPLOAD_DIR=/app/data/uploads
PROCESSING_DIR=/app/data/processing
OUTPUT_DIR=/app/data/outputs

## Prerequisites

### Server
- Ubuntu 22.04
- NVIDIA GPU
- Docker
- Docker Compose plugin
- NVIDIA Container Toolkit
- Enough disk space for models and outputs

### Recommended Hardware
- GPU with 16GB+ VRAM
- 8 vCPU minimum
- 32GB RAM recommended
- Swap configured if system RAM is limited

## Build and Run

From the project root:

docker compose build
docker compose up -d

Check status:

docker compose ps
docker ps

## Logs

### Backend
docker logs -f talkflow-backend

### Worker
docker logs -f talkflow-worker

### Nginx
docker logs -f talkflow-nginx

### Full stack logs
docker compose logs -f

## GPU Verification

### Verify GPU on the host
nvidia-smi

### Verify GPU inside Docker
docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi

If either command fails, do not continue with MuseTalk debugging until GPU access is fixed.

## Health Check After Server Reboot

After restarting the EC2 instance, verify:

docker compose ps
docker ps
nvidia-smi
docker logs --tail=200 talkflow-worker
docker logs --tail=200 talkflow-backend

The server is not healthy unless:
- Docker is running
- required containers are up
- GPU is available
- worker is healthy
- backend is healthy

## Success Criteria for Avatar Generation

A generation job is only considered successful if all of the following are true:
- MuseTalk runs without import, model, or path errors
- the worker does not fall back to static image
- a real output video file exists
- logs prove the successful end-to-end path
- the generated file is not just a placeholder static video

## Output Verification

For a given job ID:

find /app/data/outputs/<job_id> -type f | sort
ls -lh /app/data/outputs

If the worker falls back to static image, the issue is not fixed.

## Common Failure Modes

### 1. Dependency Mismatch
Typical packages involved:
- huggingface_hub
- diffusers
- transformers

Symptoms:
- import errors like cached_download
- import errors like is_offline_mode

### 2. Missing Models
Symptoms:
- MuseTalk model path errors
- missing face parsing weights
- readiness checks fail

### 3. Wrong Model Path
Symptoms:
- files exist in /app/models/...
- code checks relative paths instead

### 4. Output Discovery Failure
Symptoms:
- MuseTalk completes successfully
- worker says no MP4 found
- pipeline falls back to static image

### 5. Non-Persistent Fixes
Symptoms:
- issue seems fixed until the next reboot
- fixes were made inside running containers only
- rebuild or restart reintroduces the problem

## Production Rules

- Do not treat container-only edits as permanent fixes
- Do not bind-mount the entire repo in production unless intentionally debugging
- Do not claim success without logs and output file proof
- Prefer persistent fixes in repo, image, and mounted volumes
- Always use: verify -> fix -> verify

## Recommended Restart Policy

For long-running services, use:

restart: unless-stopped

This helps the stack recover after server restart.

## Auto-Start on Reboot

Recommended: create a systemd service that runs:

docker compose up -d

from the project directory after Docker is available.

This prevents the server from coming back without the application stack.

## Troubleshooting Checklist

Run these in order:

docker compose ps
docker ps -a
nvidia-smi
docker logs --tail=200 talkflow-worker
docker logs --tail=200 talkflow-backend
find /app/models -type f | sort
find /app/data/outputs -type f | sort

Then identify:
- which service is failing
- whether the issue is dependency, model, path, output, or restart related
- whether the fix is persistent

## Final Rule

Do not consider the deployment fixed unless a real avatar video is generated successfully with MuseTalk lipsync and without static-image fallback.
