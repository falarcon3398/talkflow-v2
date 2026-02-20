import os

def check_env():
    print("--- MuseTalk Environment Check ---")
    
    # 1. CUDA
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        print(f"CUDA Available: {cuda_available}")
        if cuda_available:
            print(f"GPU Device: {torch.cuda.get_device_name(0)}")
            print(f"CUDA Version: {torch.version.cuda}")
        else:
            print("WARNING: CUDA not found. MuseTalk requires a GPU to run efficiently.")
    except ImportError:
        print("Package 'torch': MISSING (Skipping CUDA check)")
    
    # 2. Dependencies
    pkgs = ["diffusers", "transformers", "accelerate", "cv2"]
    for pkg in pkgs:
        try:
            __import__(pkg)
            print(f"Package '{pkg}': OK")
        except ImportError:
            print(f"Package '{pkg}': MISSING")
            
    # 3. Path structure
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # MODELS_PATH is root/models/
    models_root = os.path.join(os.path.dirname(base_dir), "models")
    models_dir = os.path.join(models_root, "musetalk", "checkpoints")
    
    # Check for MuseTalk source
    try:
        from app.config import settings
        musetalk_dir = settings.MUSETALK_DIR
        print(f"MUSETALK_DIR configured as: {musetalk_dir}")
        if os.path.exists(musetalk_dir):
            print(f"Source directory found: {musetalk_dir}")
            inference_script = os.path.join(musetalk_dir, "scripts", "inference.py")
            if os.path.exists(inference_script):
                print(f"Inference script found: {inference_script}")
            else:
                print(f"ERROR: Inference script NOT found at {inference_script}")
        else:
            print(f"Source directory NOT found: {musetalk_dir}")
    except ImportError:
        print("Could not import app.config, skipping settings check.")

    required_models = [
        "musetalk/musetalk.json",
        "musetalk/pytorch_model.bin",
        "dwpose/dw-ll_ucoco_384.onnx",
        "face-parse-bisent/79999_iter.pth",
        "sd-vae-ft-mse/diffusion_pytorch_model.bin"
    ]
    
    for model in required_models:
        path = os.path.join(models_dir, model)
        if os.path.exists(path):
            print(f"Model {model}: OK")
        else:
            print(f"Model {model}: MISSING at {path}")

if __name__ == "__main__":
    check_env()
