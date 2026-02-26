from pathlib import Path
from app.config import settings
import sys
import os

# Add the project root to sys.path to allow importing from avatar_tts
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
try:
    from avatar_tts.tts_engine import generate_voiceover
except ImportError as e:
    print(f"Warning: Could not import generate_voiceover from avatar_tts: {e}")
    generate_voiceover = None

def generate_speech(text: str, voice_id: str, job_id: str, speaker_wav_path: str = None) -> str:
    """Realistic TTS using XTTS-v2 for cloning or macOS 'say' for fallback."""
    output_dir = Path(settings.PROCESSING_DIR) / job_id
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_output = output_dir / "speech.wav"
    
    if speaker_wav_path and generate_voiceover:
        try:
            print(f"CLONING: Using speaker_wav_path: {speaker_wav_path}")
            generated_wav = generate_voiceover(text, speaker_wav_path)
            shutil_copy = True
            # Move the generated file to the job output dir
            import shutil
            shutil.copy(generated_wav, str(audio_output))
            return str(audio_output)
        except Exception as e:
            print(f"CLONING ERROR: {e}, falling back to 'say'")

    try:
        # Use macOS 'say' to generate realistic audio
        import subprocess
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
