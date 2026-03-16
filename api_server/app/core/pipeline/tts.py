import os
import logging
import subprocess
import shutil
from pathlib import Path
from app.config import settings

logger = logging.getLogger(__name__)

# Try to import XTTS for voice cloning
try:
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent.parent))
    from avatar_tts.tts_engine import generate_voiceover
except ImportError as e:
    logger.warning(f"Could not import generate_voiceover from avatar_tts: {e}")
    generate_voiceover = None


def _generate_with_elevenlabs(text: str, output_path: Path, voice_id: str = None) -> bool:
    """Generate speech using ElevenLabs API."""
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    # Priority: passed voice_id > env variable > default fallback
    el_voice_id = voice_id or os.environ.get("ELEVENLABS_VOICE_ID", "bwCXcoVxWNYMlC6Esa8u")
    
    # Mapping for internal defaults to actual ElevenLabs IDs if needed
    mapping = {
        "voice_en_male_01": "pNInz6obpgmqMArAY7XM", # George
        "voice_en_female_01": "21m00Tcm4TlvDq8ikWAM" # Rachel
    }
    el_voice_id = mapping.get(el_voice_id, el_voice_id)

    if not api_key:
        return False
    try:
        import requests
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{el_voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
        }
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            mp3_path = output_path.with_suffix(".mp3")
            with open(mp3_path, "wb") as f:
                f.write(response.content)
            # Convert mp3 to wav using ffmpeg
            result = subprocess.run(
                ["ffmpeg", "-y", "-i", str(mp3_path), "-ar", "44100", "-ac", "1", str(output_path)],
                capture_output=True
            )
            mp3_path.unlink(missing_ok=True)
            if result.returncode == 0:
                logger.info(f"ElevenLabs TTS generated: {output_path}")
                return True
        logger.warning(f"ElevenLabs API error {response.status_code}: {response.text[:200]}")
        return False
    except Exception as e:
        logger.warning(f"ElevenLabs TTS failed: {e}")
        return False


def _generate_with_gtts(text: str, output_path: Path) -> bool:
    """Generate speech using gTTS (Google Text-to-Speech)."""
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang="en")
        mp3_path = output_path.with_suffix(".mp3")
        tts.save(str(mp3_path))
        # Convert mp3 to wav using ffmpeg
        result = subprocess.run(
            ["ffmpeg", "-y", "-i", str(mp3_path), "-ar", "44100", "-ac", "1", str(output_path)],
            capture_output=True
        )
        mp3_path.unlink(missing_ok=True)
        if result.returncode == 0:
            logger.info(f"gTTS generated: {output_path}")
            return True
        return False
    except Exception as e:
        logger.warning(f"gTTS failed: {e}")
        return False


def _create_silent_wav(output_path: Path, duration_secs: int = 5):
    """Create a short silent WAV as absolute last resort."""
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono",
             "-t", str(duration_secs), str(output_path)],
            capture_output=True, check=True
        )
        logger.warning(f"Created silent WAV fallback: {output_path}")
    except Exception as e:
        logger.error(f"Could not even create silent WAV: {e}")
        # Write minimal WAV header as absolute last resort
        with open(output_path, "wb") as f:
            f.write(b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00D\xac\x00\x00\x01\x00\x08\x00data\x00\x00\x00\x00')


def generate_speech(text: str, voice_id: str, job_id: str, speaker_wav_path: str = None, language: str = "en") -> str:
    """
    Generate speech audio for the given text.
    Priority order:
    1. XTTS voice cloning (if speaker_wav_path provided)
    2. ElevenLabs API
    3. gTTS (Google TTS)
    4. Silent WAV fallback
    """
    output_dir = Path(settings.PROCESSING_DIR) / job_id
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_output = output_dir / "speech.wav"

    # 1. Try XTTS voice cloning
    if speaker_wav_path and generate_voiceover:
        try:
            logger.info(f"XTTS cloning with speaker: {speaker_wav_path} (Language: {language})")
            
            # Convert MP3 to WAV if needed (XTTS/torchaudio struggles with mp3 without torchcodec)
            actual_speaker_path = speaker_wav_path
            if speaker_wav_path.lower().endswith(".mp3"):
                temp_wav = output_dir / "temp_speaker.wav"
                subprocess.run(
                    ["ffmpeg", "-y", "-i", speaker_wav_path, "-ac", "1", "-ar", "22050", str(temp_wav)],
                    capture_output=True, check=True
                )
                actual_speaker_path = str(temp_wav)

            generated = generate_voiceover(text, actual_speaker_path, language=language)
            shutil.copy(generated, str(audio_output))
            logger.info(f"XTTS cloning success: {audio_output}")
            return str(audio_output)
        except Exception as e:
            logger.warning(f"XTTS cloning failed: {e}, trying next method")
    # 2. Try ElevenLabs API
    if _generate_with_elevenlabs(text, audio_output, voice_id=voice_id):
        return str(audio_output)

    # 3. Try gTTS
    if _generate_with_gtts(text, audio_output):
        return str(audio_output)

    # 4. Silent WAV fallback (pipeline will still produce a lipsync video, just silent)
    logger.error("All TTS methods failed. Using silent WAV fallback.")
    _create_silent_wav(audio_output)
    return str(audio_output)
