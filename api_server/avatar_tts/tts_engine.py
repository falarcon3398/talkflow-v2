import os
os.environ["COQUI_TOS_AGREED"] = "1"
import time
from pathlib import Path
from TTS.api import TTS
import logging

logger = logging.getLogger(__name__)

# Global cache for the TTS model to avoid reloading on every request
_tts_model = None

def get_tts_model():
    global _tts_model
    if _tts_model is None:
        logger.info("Loading XTTS-v2 model (CPU)...")
        _tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
        # Some versions need it here, some in constructor
        _tts_model.to("cpu")
    return _tts_model

def generate_voiceover(text, speaker_wav_path, language="es"):
    """
    Generates a WAV file using XTTS-v2 for a specific speaker.
    """
    if len(text) > 300:
        raise ValueError("Text length exceeds the 300 character limit for CPU rendering.")

    if not os.path.exists(speaker_wav_path):
        raise FileNotFoundError(f"Speaker wav file not found at: {speaker_wav_path}")

    tts = get_tts_model()
    
    timestamp = int(time.time())
    output_path = Path(__file__).parent / "outputs" / "tts" / f"{timestamp}.wav"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Generating TTS for language '{language}' to {output_path}")
    
    tts.tts_to_file(
        text=text,
        speaker_wav=str(speaker_wav_path),
        language=language,
        file_path=str(output_path)
    )
    
    return str(output_path)
