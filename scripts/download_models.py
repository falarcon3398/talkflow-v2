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
        repo_id="TMElyralab/MuseTalk",
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
        repo_id="ManyOtherFunctions/face-parse-bisent",
        local_dir=str(musetalk_dir / "face-parse-bisent"),
        allow_patterns=["*.pth"]
    )

    print("--- Downloading dwpose ---")
    snapshot_download(
        repo_id="yzd-v/DWPose",
        local_dir=str(musetalk_dir / "dwpose"),
        allow_patterns=["*.onnx", "*.pth"]
    )

    print("--- Downloading GFPGAN v1.4 ---")
    gfpgan_dir = models_root / "gfpgan" / "weights"
    gfpgan_dir.mkdir(parents=True, exist_ok=True)
    # Using a reliable mirror for GFPGAN v1.4
    hf_hub_download(
        repo_id="gmk123/GFPGAN",
        filename="GFPGANv1.4.pth",
        local_dir=str(gfpgan_dir)
    )

    print("--- Models Download Complete ---")

if __name__ == "__main__":
    download_models()
