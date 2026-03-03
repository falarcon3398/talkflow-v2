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
