#!/bin/bash

# TalkFlow Cloud Setup Script
# Works on Ubuntu 22.04 with NVIDIA GPU

set -e

echo "🚀 Starting TalkFlow Cloud Setup..."

# 1. Update & Install Docker
if ! [ -x "$(command -v docker)" ]; then
    echo "📦 Installing Docker..."
    sudo apt-get update
    sudo apt-get install -y ca-certificates curl gnupg lsb-release
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
fi

# 2. Install NVIDIA Container Toolkit
if ! [ -x "$(command -v nvidia-smi)" ]; then
    echo "⚠️ NVIDIA Drivers not detected. Please install them before running this script."
    echo "Recommended: sudo apt install -y nvidia-driver-535"
else
    echo "🖥️ NVIDIA Drivers detected. Installing Toolkit..."
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
          && curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
          && curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
                sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
                sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
    sudo apt-get update
    sudo apt-get install -y nvidia-container-toolkit
    sudo nvidia-ctk runtime configure --runtime=docker
    sudo systemctl restart docker
fi

# 3. Create .env if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env from production example..."
    cp .env.production.example .env
    echo "⚠️ Please edit the .env file with your production credentials."
fi

# 4. Create required directories
mkdir -p data/uploads data/processing data/outputs models

echo "✅ Environment Ready!"
echo "👉 Run: docker compose up -d"
