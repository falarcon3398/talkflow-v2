import sys
import os
import time
import subprocess
from pathlib import Path

# Add api_server to path
sys.path.append(os.getcwd())

try:
    from app.core.pipeline_adapters.musetalk_adapter import musetalk_adapter
except ImportError:
    print("Warning: Could not import musetalk_adapter. Ensure you are running from the api_server root.")

DURATIONS = {
    "3_min": 3 * 60,
    "5_min": 5 * 60,
    "10_min": 10 * 60,
}

# Paths configured for the EC2 environment or local testing:
# Change these to point to an existing avatar and a base audio file.
# The base audio will be looped by ffmpeg to reach the target durations.
IMAGE_PATH = "/Volumes/FREDDY FILES/ANTIGRAVITY/1001-files/1001-avatar/1001-marcos-aurelio.jpg" # or path to png
BASE_AUDIO_PATH = "/Volumes/FREDDY FILES/ANTIGRAVITY/1001-files/1001-avatar/1001-audio.MP3"

def create_looped_audio(base_path: str, target_seconds: int, output_path: str):
    """
    Creates an audio file of exactly `target_seconds` by looping the base_path
    using ffmpeg's stream_loop.
    """
    print(f"Creating {target_seconds}s audio from {base_path} to {output_path}...")
    
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1",
        "-i", base_path,
        "-t", str(target_seconds),
        "-ar", "22050", # MuseTalk optimal sample rate
        "-ac", "1",     # Mono
        output_path
    ]
    
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"Created {output_path}")

def run_tests():
    # Make sure output directory exists
    os.makedirs("test_outputs", exist_ok=True)
    
    print("Starting Video Length Stress Tests (3, 5, 10 min)...")
    
    results = {}
    
    for name, seconds in DURATIONS.items():
        print(f"\n--- Starting test for {name} ({seconds}s) ---")
        audio_out = f"test_outputs/audio_{name}.wav"
        
        # 1. Create Audio Payload of Length X
        if not os.path.exists(audio_out):
            create_looped_audio(BASE_AUDIO_PATH, seconds, audio_out)
        else:
            print(f"Using existing test audio: {audio_out}")
            
        # 2. Run Inference & Time It
        start_time = time.time()
        job_id = f"stress_test_{name}"
        
        print(f"Launching MuseTalk inference for {name}...")
        try:
            # Check GPU / Memory footprint before
            os.system("nvidia-smi") if sys.platform.startswith("linux") else None
            
            result_video = musetalk_adapter.run_inference(
                avatar_path=str(Path(IMAGE_PATH).absolute()),
                audio_path=str(Path(audio_out).absolute()),
                job_id=job_id
            )
            
            # Check GPU / Memory footprint after
            os.system("nvidia-smi") if sys.platform.startswith("linux") else None

            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"SUCCESS {name}: Finished in {elapsed_time:.2f} seconds. Output: {result_video}")
            results[name] = {"status": "success", "elapsed_seconds": elapsed_time, "output": result_video}
            
        except Exception as e:
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"FAILED {name}: Errored in {elapsed_time:.2f} seconds.")
            print(f"Error: {e}")
            results[name] = {"status": "failed", "elapsed_seconds": elapsed_time, "error": str(e)}

    # Summary
    print("\n--- STRESS TEST METRICS SUMMARY ---")
    for name, r in results.items():
        print(f"{name} ({DURATIONS[name]}s Video): {r['status'].upper()} in {r['elapsed_seconds']:.2f}s")
        if r['status'] == 'success':
            # Ratio of Processing Time vs Real Duration (e.g., 2.0x means it took 10 mins to render a 5 min video)
            ratio = r['elapsed_seconds'] / DURATIONS[name]
            print(f"  └─ Compute Cost Ratio: {ratio:.2f}x Realtime")

if __name__ == "__main__":
    if not os.path.exists(IMAGE_PATH):
        print(f"Error: Avatar image not found at {IMAGE_PATH}")
        sys.exit(1)
    if not os.path.exists(BASE_AUDIO_PATH):
        print(f"Error: Base audio not found at {BASE_AUDIO_PATH}")
        sys.exit(1)
        
    run_tests()
