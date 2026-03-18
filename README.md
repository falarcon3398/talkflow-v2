# 🎬 TalkFlow Video Avatar — V2

[![React](https://img.shields.io/badge/Frontend-React%20+%20Vite-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20+%20Uvicorn-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![WebRTC](https://img.shields.io/badge/Signal-WebRTC%20+%20WebSocket-FF6F00)](https://webrtc.org/)
[![NVIDIA GPU](https://img.shields.io/badge/GPU-NVIDIA%20A10%20/%20T4-76B900?logo=nvidia&logoColor=white)](https://www.nvidia.com/)
[![Docker](https://img.shields.io/badge/DevOps-Docker%20Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

**TalkFlow Video Avatar** is a state-of-the-art, full-stack application for hyper-realistic avatar video generation. Experience low-latency, real-time "Live Calls" with AI avatars and create high-fidelity content with seamless lipsync and voice cloning.

---

## ✨ Key Features

### 🚀 **Interactive Avatar (Live Call)**
Engage in real-time conversations with your digital twin.
- **Low-Latency Streaming**: Optimized via WebRTC and WebSocket signaling.
- **Real-Time Lipsync**: Integrated MuseTalk inference on GPU clusters.
- **Adaptive Sync**: Dynamic buffer management for smooth performance.

### 🎙️ **Voice Library & Cloning**
Your voice, anywhere.
- **Voice Library Management**: Manage, clone, and assign voices to any avatar.
- **XTTS Integration**: High-fidelity cloning from short audio samples.
- **Persistent Library**: Seamless integration across the generation and interactive views.

### 🎭 **Avatar Library**
A collection of professional, high-quality avatars.
- **Video-to-Video Workflows**: Drive and animate static avatars with source videos.
- **Asset Persistence**: Centralized storage with MinIO for high availability.

### 💎 **Premium Design System**
A visually stunning, glassmorphism-inspired UI designed for modern creators.
- **Modern Typography**: Clear, accessible, and professional.
- **Responsive Layout**: Seamlessly switches between desktop and vertical (9:16) formats.

---

## 🛠️ Technology Stack

| Component | Technology |
| :--- | :--- |
| **Frontend** | React (Vite) + Tailwind (Glassmorphism) |
| **Backend API** | FastAPI + Python 3.10 |
| **Pipeline/Worker** | Celery + Redis + Redis Stream |
| **Database** | PostgreSQL |
| **Object Storage** | MinIO (AWS S3 Compatible) |
| **Inference Engine** | MuseTalk (Lip-Sync) + XTTS v2 (Voice) |
| **Real-time Comms** | WebRTC (Aiortc) + WebSockets |
| **Reverse Proxy** | Nginx (Frontend/API Gateway) |

---

## 🏗️ Repository Structure

```text
.
├── api_server/           # FastAPI application & ML Inference modules
├── frontend/             # Vite/React frontend application
├── models/               # MuseTalk & XTTS weights (mounted volume)
├── nginx/                # Reverse proxy & gateway configurations
├── scripts/              # Setup, utility, and maintenance tools
├── docker-compose.yml    # Full-stack orchestration (GPU-enabled)
└── README.md             # This guide
```

---

## 🚀 Quick Start — Recommended Deployment

This project is optimized for an **AWS EC2 g5.xlarge** or similar GPU instance running Ubuntu 22.04.

### 1. Prerequisites
- **Ubuntu 22.04 LTS**
- **NVIDIA GPU** (16GB+ VRAM recommended)
- **NVIDIA Container Toolkit** installed on the host.
- **Docker & Docker Compose**

### 2. Environment Setup
Create a `.env` file in the project root:
```env
# Database & Storage
POSTGRES_USER=talkflow
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=talkflow
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minio_secret_password

# Infrastructure
DATABASE_URL=postgresql://talkflow:secure_password@postgres:5432/talkflow
REDIS_URL=redis://redis:6379/0
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minio_secret_password

# Paths (Inside Container)
MODELS_PATH=/app/models
UPLOAD_DIR=/app/data/uploads
PROCESSING_DIR=/app/data/processing
OUTPUT_DIR=/app/data/outputs
```

### 3. Initialize Persistent Storage
Models and data must survive container rebuilds:
```bash
sudo mkdir -p /opt/talkflow/{models,data/uploads,data/processing,data/outputs}
sudo chown -R $USER:$USER /opt/talkflow
```

### 4. Build and Run
```bash
docker compose build
docker compose up -d
```

---

## 🚦 System Health & Success Criteria

### Health Checklist
1. **Container Status**: `docker compose ps` (all services UP).
2. **GPU Connectivity**: `nvidia-smi` (visible on host and inside `talkflow-worker`).
3. **Storage Access**: Models are correctly mapped and readable at `/app/models/musetalk`.

### Generation Success Definition
A job is considered **SUCCESSFUL** only if:
- [x] **MuseTalk Inference** completes without import or path errors.
- [x] **No Static Fallback**: The system does NOT default to a static image.
- [x] **Output Verified**: A real MP4 file is found in the output directory.
- [x] **Lipsync Proved**: Logs show `End-to-End processing complete` for the job ID.

---

## 🩺 Troubleshooting

| Symptom | Cause | Fix |
| :--- | :--- | :--- |
| `ImportError: cached_download` | Dependency mismatch | Ensure `huggingface_hub` version is aligned. |
| `Missing Face Parsing weights` | Missing models | Verify paths in `/opt/talkflow/models`. |
| `WebSocket connection failed` | Nginx config / Network | Check Nginx `upgrade/connection` headers. |
| `MuseTalk completes but no video` | Output Discovery | Check if path in worker matches the mounted volume. |

---

## 🛡️ Production Rules
- **PERSISTENT FIXES ONLY**: Do not edit files inside running containers. All fixes must be in the Git repo, Dockerfile, or mounted volumes.
- **LOGS ARE TRUTH**: Never claim success without showing logs that prove the end-to-end flow.
- **VERIFY TWICE**: Always run `nvidia-smi` inside the worker before starting a production run.

---

*Last updated: 2026-03-18*

