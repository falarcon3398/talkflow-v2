import asyncio
import time
import wave
from pathlib import Path
from datetime import datetime

from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
from aiortc.sdp import candidate_from_sdp
from aiortc.contrib.media import MediaBlackhole, MediaRelay
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
        
        # Tracks will be bound in set_offer to match the browser's transceivers.
        
        self.agent = VoiceAgent()
        self.vad = VADSegmenter(aggressiveness=2, frame_ms=20, end_silence_ms=800)
        self.resampler = AudioResampler(format="s16", layout="mono", rate=16000)

        # Session Recording
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = self.talk_dir / f"session_{self.session_id}"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.audio_clips: list[Path] = []

        @self.pc.on("connectionstatechange")
        def on_connectionstatechange():
            print(f"[WebRTC] Connection: {self.pc.connectionState}", flush=True)

        @self.pc.on("iceconnectionstatechange")
        def on_ice():
            print(f"[WebRTC] ICE: {self.pc.iceConnectionState}", flush=True)

        @self.pc.on("track")
        async def on_track(track):
            print(f"[LiveCall] Incoming remote track: {track.kind}", flush=True)
            if track.kind == "audio":
                asyncio.create_task(self._consume_user_audio(track))
            await self.sink.start()
        
        asyncio.create_task(self._monitor_connection())

    async def _monitor_connection(self):
        while True:
            await asyncio.sleep(5)
            if self.pc.connectionState == "closed":
                break
            print(f"[WebRTC Status] Connection: {self.pc.connectionState}, ICE: {self.pc.iceConnectionState}", flush=True)
            for i, trans in enumerate(self.pc.getTransceivers()):
                # Explicitly reporting track kind to confirm binding
                kind = trans.sender.track.kind if trans.sender.track else "None"
                print(f"  Transceiver #{i} ({trans.kind}): {trans.direction} (Track: {kind})", flush=True)

    async def _consume_user_audio(self, track):
        try:
            while True:
                frame = await track.recv()
                frames = self.resampler.resample(frame)
                for f in frames:
                    pcm = f.to_ndarray().tobytes()
                    utterances = self.vad.push(pcm)
                    for utt in utterances:
                        asyncio.create_task(self._handle_utterance(utt))
        except Exception as e:
            print(f"[LiveCall] User audio track ended: {e}", flush=True)

    async def _handle_utterance(self, pcm16_utt: bytes):
        if len(pcm16_utt) < 16000:
            return

        ts = int(time.time() * 1000)
        work_dir = self.session_dir / f"turn_{ts}"
        work_dir.mkdir(parents=True, exist_ok=True)

        try:
            print(f"[LiveCall] Processing intent ({len(pcm16_utt)/32000:.1f}s)...", flush=True)
            txt, bot_wav = await self.agent.handle_utterance_pcm(pcm16_utt, work_dir)
            
            # Track audio for recording
            user_wav = work_dir / "user.wav"
            if user_wav.exists():
                self.audio_clips.append(user_wav)
            if bot_wav and bot_wav.exists():
                self.audio_clips.append(bot_wav)
                await self.audio_track.enqueue_wav(bot_wav)

            if settings.LIPSYNC_MODE in ["wav2lip", "musetalk"]:
                out_mp4 = work_dir / "talk.mp4"
                try:
                    if settings.LIPSYNC_MODE == "musetalk":
                        from .workers import lipsync_with_musetalk
                        # Force use of photo.jpg because idle.mp4 lacks pre-computed .pkl and mmpose crashes on Mac
                        lipsync_with_musetalk(self.photo, bot_wav, out_mp4)
                    else:
                        face_input = self.idle if self.idle.exists() else self.photo
                        from .workers import lipsync_with_wav2lip
                        lipsync_with_wav2lip(face_input, bot_wav, out_mp4)
                    
                    if out_mp4.exists():
                        self.video_track.enqueue_clip_once(out_mp4)
                except Exception as e:
                    print(f"[LiveCall] Lipsync ({settings.LIPSYNC_MODE}) failed: {e}", flush=True)
        except Exception as e:
            print(f"[LiveCall] Agent error: {e}", flush=True)

    async def set_offer(self, sdp: str, type_: str):
        print(f"[LiveCall] Received Offer. Binding tracks...", flush=True)
        offer = RTCSessionDescription(sdp=sdp, type=type_)
        await self.pc.setRemoteDescription(offer)
        
        # aiortc will reuse transceivers from the offer if possible
        self.pc.addTrack(self.audio_track)
        self.pc.addTrack(self.video_track)

        for i, trans in enumerate(self.pc.getTransceivers()):
            if trans.kind == "video":
                trans.direction = "sendonly"
            elif trans.kind == "audio":
                trans.direction = "sendrecv"
            
            status = f"Track: {trans.sender.track.kind if trans.sender.track else 'None'}"
            print(f"  [Transceiver #{i}] {trans.kind} -> {trans.direction} ({status})", flush=True)

        try:
            answer = await self.pc.createAnswer()
            await self.pc.setLocalDescription(answer)
            return self.pc.localDescription
        except Exception as e:
            import traceback
            print(f"[LiveCall] Signaling error: {e}\n{traceback.format_exc()}", flush=True)
            raise

    async def add_ice_candidate(self, candidate: dict):
        # Chrome sometimes sends candidates after connection is closing or with null fields
        cand_str = candidate.get("candidate")
        if not cand_str:
            return
        
        try:
            # aiortc 1.0+ expects candidates to be parsed from SDP or built with fields
            # We strip the 'candidate:' prefix if present
            raw_cand = cand_str
            if raw_cand.startswith("candidate:"):
                raw_cand = raw_cand[10:]
            
            c = candidate_from_sdp(raw_cand)
            c.sdpMid = candidate.get("sdpMid")
            c.sdpMLineIndex = candidate.get("sdpMLineIndex")
            
            await self.pc.addIceCandidate(c)
        except Exception as e:
            print(f"[LiveCall] failed to add candidate: {e}")

    async def close(self):
        print(f"[LiveCall] Closing session {self.session_id}. Consolidating...", flush=True)
        await self.sink.stop()
        await self.pc.close()
        
        try:
            # 1. Generate History Markdown
            history_path = self.session_dir / "conversation.md"
            with open(history_path, "w", encoding="utf-8") as f:
                f.write(f"# Conversation History - Session {self.session_id}\n\n")
                for msg in self.agent.history:
                    role = msg["role"].capitalize()
                    content = msg["content"]
                    if role == "System": continue
                    f.write(f"**{role}**: {content}\n\n")
            print(f"[LiveCall] History saved: {history_path}", flush=True)

            # 2. Consolidate Audio
            if self.audio_clips:
                merged_path = self.session_dir / "full_recording.wav"
                self._merge_wavs(self.audio_clips, merged_path)
                print(f"[LiveCall] Full recording saved: {merged_path}", flush=True)
        except Exception as e:
            print(f"[LiveCall] Consolidation error: {e}", flush=True)

    def _merge_wavs(self, wav_paths: list[Path], output_path: Path):
        """Merges multiple WAVs into one using pydub."""
        from pydub import AudioSegment
        try:
            full_audio = AudioSegment.empty()
            for p in wav_paths:
                if not p.exists(): continue
                segment = AudioSegment.from_wav(str(p))
                full_audio += segment
            
            full_audio.export(str(output_path), format="wav")
            print(f"[LiveCall] MERGED record audio: {output_path}", flush=True)
        except Exception as e:
            print(f"[LiveCall] _merge_wavs error: {e}", flush=True)
