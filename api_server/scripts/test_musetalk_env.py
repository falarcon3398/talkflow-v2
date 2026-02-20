import torch
import sys
import os

def check_env():
    print("--- MuseTalk Environment Check ---")
    
    # 1. CUDA
    cuda_available = torch.cuda.is_available()
    print(f"CUDA Available: {cuda_available}")
    if cuda_available:
        print(f"GPU Device: {torch.cuda.get_device_name(0)}")
        print(f"CUDA Version: {torch.version.cuda}")
    else:
        print("WARNING: CUDA not found. MuseTalk requires a GPU to run efficiently.")
    
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
    models_dir = os.path.join(base_dir, "models", "musetalk")
    if os.path.exists(models_dir):
        print(f"Models directory found: {models_dir}")
    else:
        print(f"Models directory NOT found: {models_dir}")

if __name__ == "__main__":
    check_env()
