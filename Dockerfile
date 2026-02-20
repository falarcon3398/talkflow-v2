# Use NVIDIA CUDA base for GPU support on HF Spaces
FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

# Prevent interactive prompts during apt-get
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3.10 \
    python3-pip \
    python3-dev \
    ffmpeg \
    libsm6 \
    libxext6 \
    redis-server \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Upgrade pip and setuptools
RUN pip3 install --upgrade pip setuptools wheel

# Install Python requirements
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Make start script executable
RUN chmod +x scripts/start.sh

# Download models during build time to bake them into the image
# (Alternatively, download at runtime by moving this to start.sh if image size is an issue)
RUN python3 scripts/download_models.py

# Hugging Face Spaces expects the app on port 8000 by default (as per our README metadata)
EXPOSE 8000

# Set the entrypoint
CMD ["/bin/bash", "scripts/start.sh"]
