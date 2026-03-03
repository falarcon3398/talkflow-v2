from __future__ import annotations
import subprocess
from pathlib import Path
import time
import wave
import numpy as np
import cv2

from .settings import settings

def _make_blank_wav(path: Path, seconds: int = 2, sr: int = 16000):
    path.parent.mkdir(parents=True, exist_ok=True)
    n = seconds * sr
    samples = np.zeros(n, dtype=np.int16).tobytes()
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(samples)

def _fallback_idle_from_image(photo: Path, idle_out: Path, seconds: int, fps: int = 25):
    idle_out.parent.mkdir(parents=True, exist_ok=True)
    img = cv2.imread(str(photo))
    if img is None:
        raise RuntimeError(f"Could not read image {photo}")
    # Normalize size for stable playback
    h, w = img.shape[:2]
    target_w = 1280
    scale = target_w / max(1, w)
    target_h = int(h * scale)
    img = cv2.resize(img, (target_w, target_h))
    # center-crop to 720p
    if target_h < 720:
        pad = 720 - target_h
        img = cv2.copyMakeBorder(img, pad//2, pad - pad//2, 0, 0, cv2.BORDER_CONSTANT, value=(0,0,0))
    img = img[:720, :1280]

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    vw = cv2.VideoWriter(str(idle_out), fourcc, fps, (1280, 720))
    total = seconds * fps
    for _ in range(total):
        vw.write(img)
    vw.release()

def build_idle_with_sadtalker(photo_path: Path, idle_out: Path, seconds: int | None = None) -> None:
    """
    Try SadTalker idle build. If it fails (args mismatch), fallback to static idle loop.
    """
    seconds = seconds or settings.IDLE_SECONDS
    idle_out.parent.mkdir(parents=True, exist_ok=True)

    tmp_dir = settings.OUTPUTS_DIR / "idle_tmp" / str(int(time.time()))
    tmp_dir.mkdir(parents=True, exist_ok=True)

    blank_wav = tmp_dir / "blank.wav"
    _make_blank_wav(blank_wav, seconds=max(2, min(5, seconds)))

    # Attempt SadTalker with common args. If your launch script differs, it will fail and we fallback.
    cmd = [
        "python",
        settings.SADTALKER_PY,
        "--source_image", str(photo_path),
        "--driven_audio", str(blank_wav),
        "--result_dir", str(tmp_dir),
        "--device", settings.SADTALKER_DEVICE,
    ]

    try:
        subprocess.run(cmd, check=True)
        mp4s = list(tmp_dir.rglob("*.mp4"))
        if not mp4s:
            raise RuntimeError("SadTalker ran but no mp4 produced")
        mp4s.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        idle_out.write_bytes(mp4s[0].read_bytes())
        return
    except Exception as e:
        print("[IdleBuilder] SadTalker failed, falling back to static idle loop:", e)
        _fallback_idle_from_image(photo_path, idle_out, seconds=seconds)

def lipsync_with_wav2lip(face_video_or_image: Path, audio_wav: Path, out_mp4: Path) -> None:
    """
    Optional: Wav2Lip lipsync. Requires Wav2Lip repo + checkpoint configured.
    If not available, raises; caller can ignore and keep idle.
    """
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    if settings.LIPSYNC_MODE != "wav2lip":
        raise RuntimeError("LIPSYNC_MODE is not wav2lip")

    repo = Path(settings.WAV2LIP_REPO)
    infer_py = repo / "inference.py"
    if not infer_py.exists():
        raise RuntimeError(f"Wav2Lip inference.py not found at {infer_py}. Set WAV2LIP_REPO correctly.")

    checkpoint = Path(settings.WAV2LIP_CHECKPOINT)
    if not checkpoint.exists():
        raise RuntimeError(f"Wav2Lip checkpoint not found at {checkpoint} (put wav2lip_gan.pth on external disk).")

    cmd = [
        "python",
        str(infer_py),
        "--checkpoint_path", str(checkpoint),
        "--face", str(face_video_or_image),
        "--audio", str(audio_wav),
        "--outfile", str(out_mp4),
        "--pads", "0", "10", "0", "0",
        "--nosmooth",
        "--face_det_batch_size", str(settings.WAV2LIP_FACE_DET_BATCH),
    ]
    subprocess.run(cmd, check=True)
