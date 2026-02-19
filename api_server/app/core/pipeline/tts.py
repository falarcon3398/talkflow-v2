import subprocess
from pathlib import Path
from app.config import settings

def generate_speech(text: str, voice_id: str, job_id: str) -> str:
    """Stubbed generate_speech for local development."""
    output_dir = Path(settings.PROCESSING_DIR) / job_id
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_output = output_dir / "speech.wav"
    
    # Create empty wav file if it doesn't exist
    if not audio_output.exists():
        with open(audio_output, 'wb') as f:
            f.write(b'RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x44\xac\x00\x00\x01\x00\x08\x00data\x00\x00\x00\x00')
    
    print(f"STUB: Generated speech for {job_id} at {audio_output}")
    return str(audio_output)
