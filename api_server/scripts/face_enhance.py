import os
import cv2
import argparse
import torch
import numpy as np
from pathlib import Path
from tqdm import tqdm

def enhance_video(input_path, output_path, model_path, upscale=1):
    try:
        from gfpgan import GFPGANer
    except ImportError:
        print("Error: gfpgan package not installed. Run 'pip install gfpgan facexlib'")
        return False

    if not os.path.exists(model_path):
        print(f"Error: Model not found at {model_path}")
        return False

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    # Initialize GFPGANer
    # Use clean arch for GFPGAN v1.4
    restorer = GFPGANer(
        model_path=model_path,
        upscale=upscale,
        arch='clean',
        original_size=False,
        channel_multiplier=2,
        device=device
    )

    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {input_path}")
        return False

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) * upscale)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) * upscale)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # We use temporary directory for frames to avoid cv2.VideoWriter issues with codecs/audio
    temp_dir = Path(output_path).parent / "enhanced_temp"
    temp_dir.mkdir(parents=True, exist_ok=True)

    print(f"Enhancing {total_frames} frames...")
    for i in tqdm(range(total_frames)):
        ret, frame = cap.read()
        if not ret:
            break
        
        # Restore faces
        _, _, restored_img = restorer.enhance(
            frame,
            has_aligned=False,
            only_center_face=False,
            paste_back=True
        )
        
        # Save restored frame
        cv2.imwrite(str(temp_dir / f"{i:08d}.png"), restored_img)

    cap.release()

    # Re-assemble using ffmpeg to keep audio
    print("Re-assembling video with ffmpeg...")
    import subprocess
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-framerate", str(fps),
        "-i", str(temp_dir / "%08d.png"),
        "-i", input_path,
        "-map", "0:v:0",
        "-map", "1:a:0?",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
        "-c:a", "copy",
        output_path
    ]
    
    subprocess.run(cmd, check=True)
    
    # Cleanup temp frames
    import shutil
    shutil.rmtree(temp_dir)
    
    print(f"Success! Enhanced video saved to {output_path}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="Input video path")
    parser.add_argument("--output", type=str, required=True, help="Output video path")
    parser.add_argument("--model_path", type=str, required=True, help="GFPGAN model path")
    parser.add_argument("--upscale", type=int, default=1, help="Upscale factor")
    args = parser.parse_args()

    success = enhance_video(args.input, args.output, args.model_path, args.upscale)
    if not success:
        exit(1)
