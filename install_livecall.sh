#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# 1001-VIDEO-AVATAR: LIVE CALL (D-ID style MVP) - ONE SHOT INSTALL
# - Adds: /live UI + /api/avatars endpoints + /ws/realtime WebRTC
# - Uses: idle loop (SadTalker if possible, fallback to static loop)
# - Optional: Wav2Lip lipsync (if configured)
# - Stores heavy stuff on external disk: EXTERNAL_ROOT
# ============================================================

ROOT_DIR="$(pwd)"

# Detect backend python package root (your screenshots show api_server/app/)
if [[ -d "api_server/app" ]]; then
  PY_APP_DIR="api_server/app"
  MAIN_CANDIDATES=("api_server/app/main.py")
elif [[ -d "app" ]]; then
  PY_APP_DIR="app"
  MAIN_CANDIDATES=("app/main.py")
else
  echo "❌ Could not find api_server/app or app directory. Run this from repo root."
  exit 1
fi

# Some repos have root app.py as the entrypoint
if [[ -f "app.py" ]]; then
  MAIN_CANDIDATES+=("app.py")
fi

LIVE_DIR="$PY_APP_DIR/live_call"
STATIC_LIVE_DIR="$PY_APP_DIR/static/live"
SCRIPTS_DIR="scripts"

REQ_FILE="requirements.txt"
ENV_EXAMPLE=".env.example"
ENV_LIVECALL=".env.livecall.example"

echo "✅ Repo root: $ROOT_DIR"
echo "✅ Python app dir: $PY_APP_DIR"
echo "✅ Live module dir: $LIVE_DIR"
echo "✅ Static live dir: $STATIC_LIVE_DIR"

mkdir -p "$LIVE_DIR" "$STATIC_LIVE_DIR" "$SCRIPTS_DIR"

# ------------------------------------------------------------
# 1) Write Python module files (live_call)
# ------------------------------------------------------------
cat > "$LIVE_DIR/__init__.py" <<'PY'
from .router import router
PY

cat > "$LIVE_DIR/settings.py" <<'PY'
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
    WAV2LIP_CHECKPOINT = _env("WAV2LIP_CHECKPOINT", str((LiveCallSettings.MODELS_DIR / "wav2lip" / "wav2lip_gan.pth")))
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
PY

cat > "$LIVE_DIR/storage.py" <<'PY'
from __future__ import annotations
import json
import shutil
import uuid
from pathlib import Path
from typing import Any

from .settings import settings, ensure_external_dirs

def _avatar_dir(avatar_id: str) -> Path:
    return settings.AVATARS_DIR / avatar_id

def _meta_path(avatar_id: str) -> Path:
    return _avatar_dir(avatar_id) / "meta.json"

def _selected_path() -> Path:
    return settings.AVATARS_DIR / "selected_avatar.txt"

def init_storage():
    ensure_external_dirs()
    settings.AVATARS_DIR.mkdir(parents=True, exist_ok=True)

def create_avatar_from_upload(filename: str, file_path: Path) -> dict[str, Any]:
    init_storage()
    avatar_id = str(uuid.uuid4())
    adir = _avatar_dir(avatar_id)
    adir.mkdir(parents=True, exist_ok=True)

    ext = Path(filename).suffix.lower() or ".jpg"
    photo_path = adir / f"photo{ext}"
    shutil.copyfile(file_path, photo_path)

    meta = {"id": avatar_id, "photo": photo_path.name, "idle": "idle.mp4"}
    _meta_path(avatar_id).write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta

def list_avatars() -> list[dict[str, Any]]:
    init_storage()
    out: list[dict[str, Any]] = []
    for adir in settings.AVATARS_DIR.glob("*"):
        if not adir.is_dir():
            continue
        mp = adir / "meta.json"
        if not mp.exists():
            continue
        meta = json.loads(mp.read_text(encoding="utf-8"))
        meta["idle_ready"] = (adir / "idle.mp4").exists()
        meta["photo_url"] = f"/api/avatars/{meta['id']}/photo"
        meta["idle_url"] = f"/api/avatars/{meta['id']}/idle" if meta["idle_ready"] else None
        out.append(meta)
    out.sort(key=lambda x: x["id"])
    return out

def get_avatar(avatar_id: str) -> dict[str, Any]:
    mp = _meta_path(avatar_id)
    if not mp.exists():
        raise FileNotFoundError("Avatar not found")
    meta = json.loads(mp.read_text(encoding="utf-8"))
    meta["idle_ready"] = (_avatar_dir(avatar_id) / "idle.mp4").exists()
    return meta

def get_avatar_paths(avatar_id: str) -> dict[str, Path]:
    meta = get_avatar(avatar_id)
    adir = _avatar_dir(avatar_id)
    photo = adir / meta["photo"]
    idle = adir / "idle.mp4"
    talk_dir = adir / "talk"
    talk_dir.mkdir(parents=True, exist_ok=True)
    return {"dir": adir, "photo": photo, "idle": idle, "talk_dir": talk_dir}

def select_avatar(avatar_id: str) -> None:
    init_storage()
    _selected_path().write_text(avatar_id, encoding="utf-8")

def get_selected_avatar() -> str | None:
    p = _selected_path()
    if not p.exists():
        return None
    v = p.read_text(encoding="utf-8").strip()
    return v or None
PY

cat > "$LIVE_DIR/vad.py" <<'PY'
from __future__ import annotations
import webrtcvad

class VADSegmenter:
    def __init__(self, aggressiveness: int = 2, frame_ms: int = 20, end_silence_ms: int = 800):
        self.vad = webrtcvad.Vad(aggressiveness)
        self.frame_ms = frame_ms
        self.sample_rate = 16000
        self.bytes_per_sample = 2
        self.frame_bytes = int(self.sample_rate * (frame_ms / 1000.0) * self.bytes_per_sample)
        self.end_silence_ms = end_silence_ms

        self._in_speech = False
        self._silence_ms = 0
        self._buf = bytearray()

    def push(self, pcm: bytes) -> list[bytes]:
        utterances: list[bytes] = []
        i = 0
        while i + self.frame_bytes <= len(pcm):
            frame = pcm[i:i+self.frame_bytes]
            i += self.frame_bytes

            is_speech = self.vad.is_speech(frame, self.sample_rate)

            if is_speech:
                self._buf.extend(frame)
                self._in_speech = True
                self._silence_ms = 0
            else:
                if self._in_speech:
                    self._buf.extend(frame)
                    self._silence_ms += self.frame_ms
                    if self._silence_ms >= self.end_silence_ms:
                        utterances.append(bytes(self._buf))
                        self._buf.clear()
                        self._in_speech = False
                        self._silence_ms = 0
        return utterances
PY

cat > "$LIVE_DIR/agent.py" <<'PY'
from __future__ import annotations
from pathlib import Path
import wave
import httpx

from .settings import settings

def pcm16_to_wav(pcm_bytes: bytes, wav_path: Path, sample_rate: int = 16000) -> None:
    wav_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(wav_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_bytes)

async def openai_transcribe(wav_path: Path) -> str:
    if not settings.OPENAI_API_KEY:
        return ""
    url = f"{settings.OPENAI_BASE_URL}/audio/transcriptions"
    headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
    async with httpx.AsyncClient(timeout=120) as client:
        with wav_path.open("rb") as f:
            files = {"file": (wav_path.name, f, "audio/wav")}
            data = {"model": settings.OPENAI_STT_MODEL}
            r = await client.post(url, headers=headers, data=data, files=files)
            r.raise_for_status()
            j = r.json()
            return j.get("text", "").strip()

async def openai_chat(messages: list[dict]) -> str:
    if not settings.OPENAI_API_KEY:
        return "Set OPENAI_API_KEY in your .env to enable replies."
    url = f"{settings.OPENAI_BASE_URL}/chat/completions"
    headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": settings.OPENAI_CHAT_MODEL, "messages": messages, "temperature": 0.4}
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(url, headers=headers, json=payload)
        r.raise_for_status()
        j = r.json()
        return (j["choices"][0]["message"]["content"] or "").strip()

async def openai_tts(text: str, out_wav: Path) -> None:
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY required for OpenAI TTS")
    url = f"{settings.OPENAI_BASE_URL}/audio/speech"
    headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": settings.OPENAI_TTS_MODEL, "voice": "alloy", "input": text, "format": "wav"}
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(url, headers=headers, json=payload)
        r.raise_for_status()
        out_wav.parent.mkdir(parents=True, exist_ok=True)
        out_wav.write_bytes(r.content)

class VoiceAgent:
    def __init__(self):
        self.history = [{"role": "system", "content": settings.AGENT_SYSTEM_PROMPT}]

    async def handle_utterance_pcm(self, pcm16_utt: bytes, work_dir: Path) -> tuple[str, Path]:
        wav_in = work_dir / "user.wav"
        pcm16_to_wav(pcm16_utt, wav_in, 16000)

        user_text = await openai_transcribe(wav_in)
        if not user_text:
            user_text = "(STT not configured. Set OPENAI_API_KEY and try again.)"

        self.history.append({"role": "user", "content": user_text})
        answer = await openai_chat(self.history)
        self.history.append({"role": "assistant", "content": answer})

        wav_out = work_dir / "bot.wav"
        await openai_tts(answer, wav_out)
        return answer, wav_out
PY

cat > "$LIVE_DIR/workers.py" <<'PY'
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
PY

cat > "$LIVE_DIR/tracks.py" <<'PY'
from __future__ import annotations
import asyncio
import time
from pathlib import Path
from typing import Optional, Deque
from collections import deque

import cv2
import numpy as np
from aiortc import MediaStreamTrack
from av import VideoFrame, AudioFrame

class ClipVideoTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self, idle_source: Path, fallback_image: Path, fps: int = 25):
        super().__init__()
        self.fps = fps
        self._queue: Deque[Path] = deque()
        self._idle_source = idle_source
        self._fallback_image = fallback_image

        self._cap: Optional[cv2.VideoCapture] = None
        self._current: Optional[Path] = None
        self._next_pts = 0

        self._open_source(self._idle_source)

    def enqueue_clip_once(self, clip_path: Path):
        self._queue.append(clip_path)

    def _open_source(self, path: Path):
        if self._cap:
            self._cap.release()
            self._cap = None
        self._current = path if path.exists() else None
        if self._current and self._current.suffix.lower() in [".mp4", ".mov", ".mkv"]:
            self._cap = cv2.VideoCapture(str(self._current))
            if not self._cap.isOpened():
                self._cap = None

    async def recv(self):
        await asyncio.sleep(1 / self.fps)
        pts = self._next_pts
        self._next_pts += 1

        # switch to queued clip if currently idling
        if self._queue and (self._current == self._idle_source):
            self._open_source(self._queue.popleft())

        frame = None
        if self._cap is not None:
            ok, img = self._cap.read()
            if not ok:
                # finished talking clip -> return to idle
                self._open_source(self._idle_source)
                if self._cap:
                    ok, img = self._cap.read()
                    if ok:
                        frame = img
            else:
                frame = img

        if frame is None:
            img = cv2.imread(str(self._fallback_image))
            if img is None:
                img = np.zeros((720, 1280, 3), dtype=np.uint8)
            else:
                img = cv2.resize(img, (1280, 720))
            frame = img

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        vf = VideoFrame.from_ndarray(rgb, format="rgb24")
        vf.pts = pts
        vf.time_base = (1, self.fps)
        return vf

class QueuedAudioTrack(MediaStreamTrack):
    kind = "audio"

    def __init__(self, sample_rate: int = 48000):
        super().__init__()
        self.sample_rate = sample_rate
        self._queue: asyncio.Queue[Path] = asyncio.Queue()
        self._current = None  # tuple[np.ndarray, int]
        self._cursor = 0
        self._frame_samples = int(self.sample_rate * 0.02)
        self._next_pts = 0

    async def enqueue_wav(self, wav_path: Path):
        await self._queue.put(wav_path)

    def _load_wav(self, wav_path: Path):
        import wave
        with wave.open(str(wav_path), "rb") as wf:
            ch = wf.getnchannels()
            sr = wf.getframerate()
            sw = wf.getsampwidth()
            n = wf.getnframes()
            raw = wf.readframes(n)
        if sw != 2:
            raise RuntimeError("Only 16-bit WAV supported in this MVP")
        audio = np.frombuffer(raw, dtype=np.int16)
        if ch > 1:
            audio = audio.reshape(-1, ch)[:, 0]
        if sr != self.sample_rate:
            x = np.linspace(0, 1, num=len(audio), endpoint=False)
            x2 = np.linspace(0, 1, num=int(len(audio) * self.sample_rate / sr), endpoint=False)
            audio = np.interp(x2, x, audio).astype(np.int16)
        return audio, self.sample_rate

    async def recv(self):
        await asyncio.sleep(0.02)
        pts = self._next_pts
        self._next_pts += self._frame_samples

        if self._current is None:
            try:
                wav_path = self._queue.get_nowait()
                self._current = self._load_wav(wav_path)
                self._cursor = 0
            except asyncio.QueueEmpty:
                samples = np.zeros(self._frame_samples, dtype=np.int16)
                af = AudioFrame.from_ndarray(samples, format="s16", layout="mono")
                af.sample_rate = self.sample_rate
                af.pts = pts
                af.time_base = (1, self.sample_rate)
                return af

        audio, _sr = self._current
        end = self._cursor + self._frame_samples
        chunk = audio[self._cursor:end]
        self._cursor = end

        if len(chunk) < self._frame_samples:
            pad = np.zeros(self._frame_samples - len(chunk), dtype=np.int16)
            chunk = np.concatenate([chunk, pad])
            self._current = None

        af = AudioFrame.from_ndarray(chunk, format="s16", layout="mono")
        af.sample_rate = self.sample_rate
        af.pts = pts
        af.time_base = (1, self.sample_rate)
        return af
PY

cat > "$LIVE_DIR/webrtc.py" <<'PY'
from __future__ import annotations
import asyncio
import time
from pathlib import Path

from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
from aiortc.contrib.media import MediaBlackhole
from av.audio.resampler import AudioResampler

from .settings import settings
from .storage import get_avatar_paths
from .tracks import ClipVideoTrack, QueuedAudioTrack
from .vad import VADSegmenter
from .agent import VoiceAgent
from .workers import lipsync_with_wav2lip

class LiveCallPeer:
    def __init__(self, avatar_id: str):
        self.avatar_id = avatar_id
        self.pc = RTCPeerConnection()
        self.sink = MediaBlackhole()

        paths = get_avatar_paths(avatar_id)
        self.photo = paths["photo"]
        self.idle = paths["idle"]
        self.talk_dir = paths["talk_dir"]

        self.video_track = ClipVideoTrack(idle_source=self.idle, fallback_image=self.photo, fps=25)
        self.audio_track = QueuedAudioTrack(sample_rate=48000)
        self.agent = VoiceAgent()

        self.vad = VADSegmenter(aggressiveness=2, frame_ms=20, end_silence_ms=800)
        self.resampler = AudioResampler(format="s16", layout="mono", rate=16000)

        self.pc.addTrack(self.video_track)
        self.pc.addTrack(self.audio_track)

        @self.pc.on("track")
        async def on_track(track):
            if track.kind == "audio":
                asyncio.create_task(self._consume_user_audio(track))
            await self.sink.start()

    async def _consume_user_audio(self, track):
        while True:
            frame = await track.recv()
            frames = self.resampler.resample(frame)
            for f in frames:
                pcm = f.to_ndarray().tobytes()
                utterances = self.vad.push(pcm)
                for utt in utterances:
                    asyncio.create_task(self._handle_utterance(utt))

    async def _handle_utterance(self, pcm16_utt: bytes):
        ts = int(time.time())
        work_dir = self.talk_dir / f"turn_{ts}"
        work_dir.mkdir(parents=True, exist_ok=True)

        try:
            _answer_text, bot_wav = await self.agent.handle_utterance_pcm(pcm16_utt, work_dir)

            await self.audio_track.enqueue_wav(bot_wav)

            if settings.LIPSYNC_MODE == "wav2lip":
                out_mp4 = work_dir / "talk.mp4"
                try:
                    face_input = self.idle if self.idle.exists() else self.photo
                    lipsync_with_wav2lip(face_input, bot_wav, out_mp4)
                    self.video_track.enqueue_clip_once(out_mp4)
                except Exception as e:
                    print("[LiveCall] Wav2Lip failed (continuing idle):", e)

        except Exception as e:
            print("[LiveCall] error handling utterance:", e)

    async def set_offer(self, sdp: str, type_: str):
        offer = RTCSessionDescription(sdp=sdp, type=type_)
        await self.pc.setRemoteDescription(offer)
        answer = await self.pc.createAnswer()
        await self.pc.setLocalDescription(answer)
        return self.pc.localDescription

    async def add_ice_candidate(self, candidate: dict):
        c = RTCIceCandidate(
            sdpMid=candidate.get("sdpMid"),
            sdpMLineIndex=candidate.get("sdpMLineIndex"),
            candidate=candidate.get("candidate"),
        )
        await self.pc.addIceCandidate(c)

    async def close(self):
        await self.sink.stop()
        await self.pc.close()
PY

cat > "$LIVE_DIR/router.py" <<'PY'
from __future__ import annotations
import asyncio
import json
import tempfile
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from .settings import settings, ensure_external_dirs
from .storage import (
    init_storage, create_avatar_from_upload, list_avatars, get_avatar_paths,
    select_avatar, get_selected_avatar, get_avatar
)
from .workers import build_idle_with_sadtalker
from .webrtc import LiveCallPeer

router = APIRouter()

@router.get("/api/avatars")
def api_list_avatars():
    return {"avatars": list_avatars(), "selected": get_selected_avatar()}

@router.post("/api/avatars/upload")
async def api_upload_avatar(file: UploadFile = File(...)):
    init_storage()
    suffix = Path(file.filename).suffix or ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = Path(tmp.name)

    meta = create_avatar_from_upload(file.filename, tmp_path)
    return meta

@router.post("/api/avatars/{avatar_id}/select")
def api_select_avatar(avatar_id: str):
    try:
        _ = get_avatar(avatar_id)
    except FileNotFoundError:
        raise HTTPException(404, "Avatar not found")
    select_avatar(avatar_id)
    return {"ok": True, "selected": avatar_id}

@router.get("/api/avatars/{avatar_id}/photo")
def api_get_photo(avatar_id: str):
    paths = get_avatar_paths(avatar_id)
    if not paths["photo"].exists():
        raise HTTPException(404, "Photo not found")
    return FileResponse(paths["photo"])

@router.get("/api/avatars/{avatar_id}/idle")
def api_get_idle(avatar_id: str):
    paths = get_avatar_paths(avatar_id)
    if not paths["idle"].exists():
        raise HTTPException(404, "Idle not ready")
    return FileResponse(paths["idle"])

@router.post("/api/avatars/{avatar_id}/build-idle")
async def api_build_idle(avatar_id: str):
    paths = get_avatar_paths(avatar_id)
    if paths["idle"].exists():
        return {"ok": True, "idle_ready": True}

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, build_idle_with_sadtalker, paths["photo"], paths["idle"], settings.IDLE_SECONDS)
    return {"ok": True, "idle_ready": True}

@router.websocket("/ws/realtime")
async def ws_realtime(ws: WebSocket):
    await ws.accept()

    avatar_id = ws.query_params.get("avatar_id") or get_selected_avatar()
    if not avatar_id:
        await ws.send_text(json.dumps({"type": "error", "message": "No avatar selected. Upload/select an avatar first."}))
        await ws.close()
        return

    peer = LiveCallPeer(avatar_id=avatar_id)

    @peer.pc.on("icecandidate")
    async def on_icecandidate(candidate):
        if candidate is None:
            return
        await ws.send_text(json.dumps({
            "type": "candidate",
            "candidate": {
                "candidate": candidate.candidate,
                "sdpMid": candidate.sdpMid,
                "sdpMLineIndex": candidate.sdpMLineIndex,
            }
        }))

    try:
        while True:
            msg = await ws.receive_text()
            data = json.loads(msg)

            if data.get("type") == "offer":
                desc = await peer.set_offer(data["sdp"], data["sdpType"])
                await ws.send_text(json.dumps({"type": "answer", "sdp": desc.sdp, "sdpType": desc.type}))

            elif data.get("type") == "candidate":
                await peer.add_ice_candidate(data["candidate"])

            elif data.get("type") == "ping":
                await ws.send_text(json.dumps({"type": "pong"}))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print("[ws_realtime] error:", e)
    finally:
        await peer.close()
PY

# ------------------------------------------------------------
# 2) Write static UI files (/live)
# ------------------------------------------------------------
cat > "$STATIC_LIVE_DIR/index.html" <<'HTML'
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Live Call - Talking Head</title>
  <link rel="stylesheet" href="./style.css">
</head>
<body>
  <div class="wrap">
    <h1>LIVE CALL (D-ID style MVP)</h1>

    <section class="card">
      <h2>1) Avatars (ver fotos)</h2>
      <div class="row">
        <input id="file" type="file" accept="image/*" />
        <button id="upload">Upload</button>
        <button id="refresh">Refresh</button>
      </div>
      <div id="avatars" class="grid"></div>
    </section>

    <section class="card">
      <h2>2) Call</h2>
      <div class="row">
        <button id="start">Start Call</button>
        <button id="end" disabled>End</button>
        <span id="status" class="status">Idle</span>
      </div>

      <div class="videoWrap">
        <video id="remoteVideo" autoplay playsinline></video>
      </div>

      <p class="hint">
        Tip: Para producción agrega TURN (coturn). Para pruebas, local o misma red suele funcionar con STUN.
      </p>
    </section>
  </div>

  <script src="./livecall.js"></script>
</body>
</html>
HTML

cat > "$STATIC_LIVE_DIR/style.css" <<'CSS'
body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; background:#0b0f14; color:#e8eef6; margin:0; }
.wrap { max-width: 980px; margin: 24px auto; padding: 0 16px; }
h1 { font-size: 20px; margin: 0 0 16px; }
.card { background:#121a24; border:1px solid #203044; border-radius: 14px; padding:16px; margin-bottom:16px; }
.row { display:flex; gap:10px; align-items:center; flex-wrap:wrap; }
button { background:#2a76ff; color:white; border:0; padding:10px 12px; border-radius:10px; cursor:pointer; }
button:disabled { background:#334155; cursor:not-allowed; }
.status { padding: 6px 10px; background:#0f172a; border:1px solid #22324a; border-radius:999px; }
.grid { display:grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap:12px; margin-top:12px; }
.tile { border:1px solid #22324a; border-radius:12px; padding:10px; background:#0f172a; }
.tile img { width:100%; border-radius:10px; display:block; }
.tile .actions { display:flex; gap:8px; margin-top:8px; flex-wrap:wrap; }
.tile .small { background:#1f2937; }
.videoWrap { margin-top: 10px; background:#0f172a; border:1px solid #22324a; border-radius:12px; padding:10px; }
video { width: 100%; border-radius: 10px; background:black; }
.hint { opacity: 0.8; font-size: 13px; }
CSS

cat > "$STATIC_LIVE_DIR/livecall.js" <<'JS'
let selectedAvatar = null;
let ws = null;
let pc = null;
let localStream = null;

const $ = (id) => document.getElementById(id);
const avatarsEl = $("avatars");
const statusEl = $("status");
const remoteVideo = $("remoteVideo");

function setStatus(s) { statusEl.textContent = s; }

async function refreshAvatars() {
  const r = await fetch("/api/avatars");
  const j = await r.json();
  selectedAvatar = j.selected || null;

  avatarsEl.innerHTML = "";
  for (const a of j.avatars) {
    const div = document.createElement("div");
    div.className = "tile";

    const img = document.createElement("img");
    img.src = a.photo_url;
    div.appendChild(img);

    const info = document.createElement("div");
    info.style.marginTop = "8px";
    info.textContent = `id: ${a.id.slice(0, 8)}...  idle: ${a.idle_ready ? "✅" : "⏳"}`;
    div.appendChild(info);

    const actions = document.createElement("div");
    actions.className = "actions";

    const btnSelect = document.createElement("button");
    btnSelect.textContent = (selectedAvatar === a.id) ? "Selected" : "Select";
    btnSelect.className = "small";
    btnSelect.onclick = async () => {
      await fetch(`/api/avatars/${a.id}/select`, { method: "POST" });
      await refreshAvatars();
    };

    const btnIdle = document.createElement("button");
    btnIdle.textContent = a.idle_ready ? "Idle Ready" : "Build Idle";
    btnIdle.disabled = a.idle_ready;
    btnIdle.onclick = async () => {
      btnIdle.disabled = true;
      btnIdle.textContent = "Building...";
      await fetch(`/api/avatars/${a.id}/build-idle`, { method: "POST" });
      await refreshAvatars();
    };

    actions.appendChild(btnSelect);
    actions.appendChild(btnIdle);
    div.appendChild(actions);

    avatarsEl.appendChild(div);
  }
}

async function uploadAvatar() {
  const file = $("file").files?.[0];
  if (!file) return alert("Select an image first.");
  const fd = new FormData();
  fd.append("file", file);
  await fetch("/api/avatars/upload", { method: "POST", body: fd });
  await refreshAvatars();
}

async function startCall() {
  if (!selectedAvatar) return alert("Select an avatar first.");
  setStatus("Connecting...");

  ws = new WebSocket(`${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/ws/realtime?avatar_id=${selectedAvatar}`);

  pc = new RTCPeerConnection({
    iceServers: [{ urls: "stun:stun.l.google.com:19302" }]
  });

  pc.ontrack = (ev) => {
    const [stream] = ev.streams;
    remoteVideo.srcObject = stream;
  };

  pc.onicecandidate = (ev) => {
    if (ev.candidate && ws?.readyState === 1) {
      ws.send(JSON.stringify({ type: "candidate", candidate: ev.candidate }));
    }
  };

  localStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
  for (const t of localStream.getTracks()) pc.addTrack(t, localStream);

  ws.onmessage = async (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.type === "answer") {
      await pc.setRemoteDescription({ type: msg.sdpType, sdp: msg.sdp });
      setStatus("Live (Speak normally)");
      $("start").disabled = true;
      $("end").disabled = false;
    }
    if (msg.type === "candidate") {
      try { await pc.addIceCandidate(msg.candidate); } catch (e) {}
    }
    if (msg.type === "error") {
      alert(msg.message || "Error");
    }
  };

  ws.onopen = async () => {
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);
    ws.send(JSON.stringify({ type: "offer", sdp: offer.sdp, sdpType: offer.type }));
  };

  ws.onclose = () => setStatus("Closed");
}

async function endCall() {
  setStatus("Closing...");
  try { localStream?.getTracks()?.forEach(t => t.stop()); } catch {}
  try { pc?.close(); } catch {}
  try { ws?.close(); } catch {}
  pc = null; ws = null; localStream = null;
  remoteVideo.srcObject = null;
  $("start").disabled = false;
  $("end").disabled = true;
  setStatus("Idle");
}

$("upload").onclick = uploadAvatar;
$("refresh").onclick = refreshAvatars;
$("start").onclick = startCall;
$("end").onclick = endCall;

refreshAvatars();
JS

# ------------------------------------------------------------
# 3) External storage helper (scripts/setup_external_storage.sh)
# ------------------------------------------------------------
cat > "$SCRIPTS_DIR/setup_external_storage.sh" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
EXTERNAL_ROOT="${EXTERNAL_ROOT:-/mnt/external/1001-video-avatar}"

echo "Using EXTERNAL_ROOT=$EXTERNAL_ROOT"
mkdir -p "$EXTERNAL_ROOT"/{models,outputs,caches,logs,avatars,hf_cache,torch_cache,pip_cache,npm_cache}

export HF_HOME="$EXTERNAL_ROOT/hf_cache"
export TRANSFORMERS_CACHE="$EXTERNAL_ROOT/hf_cache"
export TORCH_HOME="$EXTERNAL_ROOT/torch_cache"
export XDG_CACHE_HOME="$EXTERNAL_ROOT/caches"
export PIP_CACHE_DIR="$EXTERNAL_ROOT/pip_cache"
export npm_config_cache="$EXTERNAL_ROOT/npm_cache"

echo "Set these env vars in your shell or .env:"
echo "EXTERNAL_ROOT=$EXTERNAL_ROOT"
echo "HF_HOME=$HF_HOME"
echo "TRANSFORMERS_CACHE=$TRANSFORMERS_CACHE"
echo "TORCH_HOME=$TORCH_HOME"
echo "XDG_CACHE_HOME=$XDG_CACHE_HOME"
echo "PIP_CACHE_DIR=$PIP_CACHE_DIR"
echo "npm_config_cache=$npm_config_cache"
echo "Done."
SH
chmod +x "$SCRIPTS_DIR/setup_external_storage.sh"

# ------------------------------------------------------------
# 4) Update requirements.txt (append only if missing)
# ------------------------------------------------------------
touch "$REQ_FILE"

add_req() {
  local line="$1"
  if ! grep -qF "$line" "$REQ_FILE"; then
    echo "$line" >> "$REQ_FILE"
  fi
}

add_req "aiortc==1.7.0"
add_req "av>=11.0.0"
add_req "opencv-python>=4.8.0"
add_req "webrtcvad>=2.0.10"
add_req "httpx>=0.27.0"
add_req "python-multipart>=0.0.9"

# ------------------------------------------------------------
# 5) Write .env livecall example (single file, no merge conflicts)
# ------------------------------------------------------------
cat > "$ENV_LIVECALL" <<'ENV'
# Live Call (D-ID style MVP)
LIVE_CALL_ENABLED=1
EXTERNAL_ROOT=/mnt/external/1001-video-avatar

OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_STT_MODEL=whisper-1
OPENAI_TTS_MODEL=gpt-4o-mini-tts

# SadTalker idle builder
SADTALKER_PY=launch_sadtalker.py
SADTALKER_DEVICE=cuda
IDLE_SECONDS=4

# Lipsync live (optional)
LIPSYNC_MODE=wav2lip
WAV2LIP_REPO=/absolute/path/to/wav2lip
WAV2LIP_CHECKPOINT=/mnt/external/1001-video-avatar/models/wav2lip/wav2lip_gan.pth
WAV2LIP_FACE_DET_BATCH=16
ENV

# ------------------------------------------------------------
# 6) Patch main entrypoint(s) to include router + mount /live
#    Safe approach: append block that only runs if imports succeed.
# ------------------------------------------------------------
PATCH_BLOCK=$(cat <<'PY'
# ------------------- LIVE CALL (auto-added) -------------------
try:
    from pathlib import Path as _Path
    from fastapi.staticfiles import StaticFiles as _StaticFiles
    from app.live_call import router as _live_router
    from app.live_call.settings import ensure_external_dirs as _ensure_external_dirs

    _ensure_external_dirs()

    # Add API routes + WebRTC ws
    try:
        app.include_router(_live_router)
    except Exception:
        # if your FastAPI instance is named differently, adjust manually
        pass

    # Mount /live static UI (served by backend)
    _live_static_dir = _Path(__file__).resolve().parent / "static" / "live"
    if _live_static_dir.exists():
        try:
            app.mount("/live", _StaticFiles(directory=str(_live_static_dir), html=True), name="live")
        except Exception:
            pass
except Exception as _e:
    print("[LIVE CALL] not enabled or failed to load:", _e)
# ----------------- END LIVE CALL (auto-added) -----------------
PY
)

patched_any=false
for f in "${MAIN_CANDIDATES[@]}"; do
  if [[ -f "$f" ]]; then
    if grep -q "LIVE CALL (auto-added)" "$f"; then
      echo "ℹ️  Already patched: $f"
      patched_any=true
      continue
    fi
    # Only patch files that likely define FastAPI app
    if grep -q "FastAPI" "$f"; then
      echo "" >> "$f"
      echo "$PATCH_BLOCK" >> "$f"
      echo "✅ Patched: $f"
      patched_any=true
    else
      echo "⚠️  Skipped (no FastAPI found): $f"
    fi
  fi
done

if [[ "$patched_any" == "false" ]]; then
  echo "⚠️  Could not auto-patch a main FastAPI file. Add this manually in your FastAPI entrypoint:"
  echo "$PATCH_BLOCK"
fi

# ------------------------------------------------------------
# 7) Final instructions
# ------------------------------------------------------------
echo ""
echo "✅ INSTALL COMPLETE"
echo ""
echo "NEXT STEPS:"
echo "1) External disk (recommended):"
echo "   export EXTERNAL_ROOT=/mnt/external/1001-video-avatar"
echo "   ./scripts/setup_external_storage.sh"
echo ""
echo "2) Install Python deps:"
echo "   pip install -r requirements.txt"
echo ""
echo "3) Run backend (choose the same command you use today):"
echo "   - If you run from api_server/: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo "   - Or your current command"
echo ""
echo "4) Open UI:"
echo "   http://localhost:8000/live"
echo ""
echo "NOTES:"
echo "- This MVP uses OpenAI STT/LLM/TTS if OPENAI_API_KEY is set."
echo "- Idle video tries SadTalker first, then falls back to a static loop if SadTalker args mismatch."
echo "- Wav2Lip is optional: set LIPSYNC_MODE=none to disable lipsync."
echo "- Put heavy models/checkpoints under EXTERNAL_ROOT (see .env.livecall.example)."
echo ""
