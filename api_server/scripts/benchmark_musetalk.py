import sys
import os
from pathlib import Path

# Add api_server to path
sys.path.append(os.getcwd())

from app.core.pipeline_adapters.musetalk_adapter import musetalk_adapter
from app.config import settings

def run_benchmark():
    image_path = "/Volumes/FREDDY FILES/ANTIGRAVITY/1001-files/1001-avatar/1001-marcos-aurelio.png"
    audio_path = "/Volumes/FREDDY FILES/ANTIGRAVITY/1001-files/1001-avatar/1001-audio.wav"
    job_id = "benchmark_1"
    
    print(f"--- Running MuseTalk Benchmark for job {job_id} ---")
    print(f"Image: {image_path}")
    print(f"Audio: {audio_path}")
    
    result = musetalk_adapter.run_inference(
        avatar_path=str(Path(image_path).absolute()),
        audio_path=str(Path(audio_path).absolute()),
        job_id=job_id
    )
    
    if result:
        print(f"SUCCESS: Result saved to {result}")
    else:
        print("FAILURE: MuseTalk inference failed.")

if __name__ == "__main__":
    run_benchmark()
