import subprocess
from pathlib import Path
from app.config import settings

def generate_speech(text: str, voice_id: str, job_id: str) -> str:
    """
    Wrapper for Piper TTS.
    """
    models_dir = Path(settings.MODELS_PATH) / "piper"
    output_dir = Path(settings.PROCESSING_DIR) / job_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    audio_output = output_dir / "speech.wav"
    voice_model = models_dir / f"{voice_id}.onnx"
    
    # Check if model exists, if not use fallback or raise error
    if not voice_model.exists():
        # For MVP development, we might just use a placeholder or log failure
        pass

    # Command implementation as per PRD
    cmd = [
        "piper",
        "--model", str(voice_model),
        "--output_file", str(audio_output)
    ]
    
    try:
        subprocess.run(cmd, input=text.encode(), check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"Piper TTS failed: {e.stderr.decode()}")
        # In a real dev env, we'd handle missing models here
        raise

    return str(audio_output)
