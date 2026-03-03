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
