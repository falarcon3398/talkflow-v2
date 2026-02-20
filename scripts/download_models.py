import os
from huggingface_hub import hf_hub_download, snapshot_download
from pathlib import Path

def download_models():
    models_root = Path("models")
    musetalk_dir = models_root / "musetalk" / "checkpoints"
    musetalk_dir.mkdir(parents=True, exist_ok=True)

    print("--- Downloading MuseTalk Weights ---")
    # MuseTalk Weights
    snapshot_download(
        repo_id="TencentGameMate/MuseTalk",
        local_dir=str(musetalk_dir),
        ignore_patterns=["*.md", "*.txt", ".git*"]
    )

    print("--- Downloading SD-VAE-FT-MSE ---")
    # SD VAE
    snapshot_download(
        repo_id="stabilityai/sd-vae-ft-mse",
        local_dir=str(musetalk_dir / "sd-vae-ft-mse"),
        ignore_patterns=["*.md", "README.md", "LICENSE"]
    )

    print("--- Downloading Whisper Tiny ---")
    # Whisper Tiny
    snapshot_download(
        repo_id="openai/whisper-tiny",
        local_dir=str(musetalk_dir / "whisper"),
        ignore_patterns=["*.md", "README.md", "LICENSE"]
    )

    print("--- Downloading face-parsing ---")
    snapshot_download(
        repo_id="pwwu/face-parse-bisent",
        local_dir=str(musetalk_dir / "face-parse-bisent")
    )

    print("--- Downloading dwpose ---")
    snapshot_download(
        repo_id="pwwu/dwpose",
        local_dir=str(musetalk_dir / "dwpose")
    )

    print("--- Models Download Complete ---")

if __name__ == "__main__":
    download_models()
