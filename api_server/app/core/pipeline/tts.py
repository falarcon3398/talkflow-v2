import subprocess
from pathlib import Path
from app.config import settings

def generate_speech(text: str, voice_id: str, job_id: str) -> str:
    """Realistic TTS stub using macOS 'say' command."""
    output_dir = Path(settings.PROCESSING_DIR) / job_id
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_output = output_dir / "speech.wav"
    
    try:
        # Use macOS 'say' to generate realistic audio
        # We use LEI16@44100 for high quality WAV compatibility
        subprocess.run([
            "say", text, "-o", str(audio_output), "--data-format=LEI16@44100"
        ], check=True)
        print(f"REAL STUB: Generated speech using 'say' for {job_id}")
    except Exception as e:
        print(f"FALLBACK: Error using 'say', creating empty WAV: {str(e)}")
        if not audio_output.exists():
            with open(audio_output, 'wb') as f:
                f.write(b'RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x44\xac\x00\x00\x01\x00\x08\x00data\x00\x00\x00\x00')
    
    return str(audio_output)
