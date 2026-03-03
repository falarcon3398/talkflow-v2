from __future__ import annotations
import os
from pathlib import Path

def _env(key: str, default: str | None = None) -> str | None:
    v = os.getenv(key)
    return v if v not in (None, "") else default

class LiveCallSettings:
    EXTERNAL_ROOT = Path(_env("EXTERNAL_ROOT", "/mnt/external/1001-video-avatar")).resolve()

    AVATARS_DIR = EXTERNAL_ROOT / "avatars"
    MODELS_DIR = EXTERNAL_ROOT / "models"
    OUTPUTS_DIR = EXTERNAL_ROOT / "outputs"
    CACHE_DIR = EXTERNAL_ROOT / "caches"
    LOGS_DIR = EXTERNAL_ROOT / "logs"

    LIVE_CALL_ENABLED = _env("LIVE_CALL_ENABLED", "1") == "1"

    OPENAI_API_KEY = _env("OPENAI_API_KEY", "")
    OPENAI_BASE_URL = _env("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_CHAT_MODEL = _env("OPENAI_CHAT_MODEL", "gpt-4o-mini")
    OPENAI_STT_MODEL = _env("OPENAI_STT_MODEL", "whisper-1")
    OPENAI_TTS_MODEL = _env("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")

    AGENT_SYSTEM_PROMPT = _env(
        "AGENT_SYSTEM_PROMPT",
        "You are a helpful assistant. Keep answers concise, friendly, and clear."
    )

    # SadTalker (idle builder)
    SADTALKER_PY = _env("SADTALKER_PY", "launch_sadtalker.py")  # your repo has launch_sadtalker.py
    SADTALKER_DEVICE = _env("SADTALKER_DEVICE", "cuda")
    IDLE_SECONDS = int(_env("IDLE_SECONDS", "4"))

    # Lipsync live (optional)
    LIPSYNC_MODE = _env("LIPSYNC_MODE", "wav2lip")  # wav2lip | none
    WAV2LIP_REPO = _env("WAV2LIP_REPO", str((Path.cwd() / "wav2lip").resolve()))
    # Note: WAV2LIP_CHECKPOINT is resolved lazily to avoid self-referencing during class body definition
    _wav2lip_default = str(
        Path(_env("EXTERNAL_ROOT", "/mnt/external/1001-video-avatar")).resolve()
        / "models" / "wav2lip" / "wav2lip_gan.pth"
    )
    WAV2LIP_CHECKPOINT = _env("WAV2LIP_CHECKPOINT", _wav2lip_default)
    WAV2LIP_FACE_DET_BATCH = int(_env("WAV2LIP_FACE_DET_BATCH", "16"))

settings = LiveCallSettings()

def ensure_external_dirs() -> None:
    for p in [
        settings.EXTERNAL_ROOT,
        settings.AVATARS_DIR,
        settings.MODELS_DIR,
        settings.OUTPUTS_DIR,
        settings.CACHE_DIR,
        settings.LOGS_DIR,
    ]:
        p.mkdir(parents=True, exist_ok=True)
