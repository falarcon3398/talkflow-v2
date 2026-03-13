import os
os.environ["COQUI_TOS_AGREED"] = "1"
import time
from pathlib import Path
from TTS.api import TTS
import logging

logger = logging.getLogger(__name__)

import torch

# Fix for newer PyTorch versions (2.6+) that require explicit global allowlisting
try:
    from TTS.tts.configs.xtts_config import XttsConfig
    if hasattr(torch.serialization, 'add_safe_globals'):
        torch.serialization.add_safe_globals([XttsConfig])
except ImportError:
    pass

# Global cache for the TTS model to avoid reloading on every request
_tts_model = None

def get_tts_model():
    global _tts_model
    if _tts_model is None:
        use_gpu = torch.cuda.is_available()
        logger.info(f"Loading XTTS-v2 model (GPU={use_gpu})...")
        try:
            _tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=use_gpu)
        except Exception as e:
            logger.error(f"Failed to load XTTS model on GPU={use_gpu}: {e}")
            if use_gpu:
                logger.info("Retrying XTTS load on CPU...")
                _tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
            else:
                raise
    return _tts_model

def generate_voiceover(text, speaker_wav_path, language="es"):
    """
    Generates a WAV file using XTTS-v2 for a specific speaker.
    """
    if len(text) > 500:
        raise ValueError("Text length exceeds the 500 character limit.")

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
