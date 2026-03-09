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
    print(f"[Agent] Transcription start for {wav_path}", flush=True)
    if not settings.OPENAI_API_KEY:
        print("[Agent] STT skip: No API KEY", flush=True)
        return ""
    url = f"{settings.OPENAI_BASE_URL}/audio/transcriptions"
    headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
    async with httpx.AsyncClient(timeout=60) as client:
        try:
            # Read into memory to avoid Content-Length instability on external disk
            wav_data = wav_path.read_bytes()
            files = {"file": (wav_path.name, wav_data, "audio/wav")}
            data = {"model": settings.OPENAI_STT_MODEL}
            print(f"[Agent] Sending STT request to {url}... ({len(wav_data)} bytes)", flush=True)
            r = await client.post(url, headers=headers, data=data, files=files)
            print(f"[Agent] STT response status: {r.status_code}", flush=True)
            if r.status_code != 200:
                print(f"[Agent] STT Error {r.status_code}: {r.text}", flush=True)
                return ""
            j = r.json()
            text = j.get("text", "").strip()
            print(f"[Agent] STT result: '{text}'", flush=True)
            return text
        except Exception as e:
            print(f"[Agent] STT Exception: {e}", flush=True)
            return ""

async def openai_chat(messages: list[dict]) -> str:
    if not settings.OPENAI_API_KEY:
        return "Set OPENAI_API_KEY in your .env to enable replies."
    url = f"{settings.OPENAI_BASE_URL}/chat/completions"
    headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": settings.OPENAI_CHAT_MODEL, "messages": messages, "temperature": 0.4}
    async with httpx.AsyncClient(timeout=60) as client:
        print(f"[Agent] Sending Chat request to {url}...", flush=True)
        try:
            r = await client.post(url, headers=headers, json=payload)
            print(f"[Agent] Chat response status: {r.status_code}", flush=True)
            if r.status_code != 200:
                print(f"[Agent] Chat Error {r.status_code}: {r.text}", flush=True)
                return "Error in chat."
            j = r.json()
            answer = (j["choices"][0]["message"]["content"] or "").strip()
            print(f"[Agent] Chat result: '{answer[:50]}...'", flush=True)
            return answer
        except Exception as e:
            print(f"[Agent] Chat Exception: {e}", flush=True)
            return "Exception in chat."

async def openai_tts(text: str, out_wav: Path) -> None:
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY required for OpenAI TTS")
    url = f"{settings.OPENAI_BASE_URL}/audio/speech"
    headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": settings.OPENAI_TTS_MODEL, "voice": "alloy", "input": text, "response_format": "wav"}
    async with httpx.AsyncClient(timeout=60) as client:
        print(f"[Agent] Sending TTS request to {url}...", flush=True)
        try:
            r = await client.post(url, headers=headers, json=payload)
            print(f"[Agent] TTS response status: {r.status_code}", flush=True)
            if r.status_code != 200:
                print(f"[Agent] TTS Error {r.status_code}: {r.text}", flush=True)
                return
            out_wav.parent.mkdir(parents=True, exist_ok=True)
            out_wav.write_bytes(r.content)
            print(f"[Agent] TTS saved: {out_wav}", flush=True)
        except Exception as e:
            print(f"[Agent] TTS Exception: {e}", flush=True)

async def elevenlabs_tts(text: str, out_wav: Path) -> None:
    if not settings.ELEVENLABS_API_KEY:
        print("[Agent] ElevenLabs skip: No API KEY", flush=True)
        return

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{settings.ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": settings.ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": settings.ELEVENLABS_MODEL_ID,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    async with httpx.AsyncClient(timeout=60) as client:
        print(f"[Agent] Sending ElevenLabs TTS request...", flush=True)
        try:
            r = await client.post(url, headers=headers, json=payload)
            print(f"[Agent] ElevenLabs TTS response status: {r.status_code}", flush=True)
            if r.status_code != 200:
                print(f"[Agent] ElevenLabs Error {r.status_code}: {r.text}", flush=True)
                return

            # ElevenLabs returns MP3 (regardless of output_format request).
            # We must convert it to PCM WAV so PyAV can decode it as raw audio frames.
            import tempfile, av as _av, numpy as np
            audio_bytes = r.content
            content_type = r.headers.get("content-type", "")
            print(f"[Agent] ElevenLabs content-type: {content_type}, bytes: {len(audio_bytes)}", flush=True)

            # Write the raw response (MP3 or PCM) to a temp file and decode with PyAV
            suffix = ".mp3" if "mpeg" in content_type else ".wav"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name

            try:
                container = _av.open(tmp_path)
                resampler = _av.audio.resampler.AudioResampler(format="s16", layout="mono", rate=44100)
                chunks = []
                for frame in container.decode(audio=0):
                    for f in resampler.resample(frame):
                        chunks.append(f.to_ndarray().flatten())
                container.close()

                if chunks:
                    audio = np.concatenate(chunks)
                    pcm16_to_wav(audio.tobytes(), out_wav, sample_rate=44100)
                    print(f"[Agent] ElevenLabs TTS saved as WAV: {out_wav} ({len(audio)/44100:.1f}s)", flush=True)
                else:
                    print("[Agent] ElevenLabs: no audio frames decoded", flush=True)
            finally:
                import os
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

        except Exception as e:
            print(f"[Agent] ElevenLabs TTS Exception: {e}", flush=True)

class VoiceAgent:
    def __init__(self):
        self.history = [{"role": "system", "content": settings.AGENT_SYSTEM_PROMPT}]
        key_show = (settings.OPENAI_API_KEY[:6] + "...") if settings.OPENAI_API_KEY else "MISSING"
        print(f"[Agent] Initialized with key: {key_show}", flush=True)

    async def handle_utterance_pcm(self, pcm16_utt: bytes, work_dir: Path) -> tuple[str, Path]:
        wav_in = work_dir / "user.wav"
        pcm16_to_wav(pcm16_utt, wav_in, 16000)
        print(f"[Agent] Saved temporary WAV: {wav_in}", flush=True)

        user_text = await openai_transcribe(wav_in)
        if not user_text:
            return "(STT failed)", None

        self.history.append({"role": "user", "content": user_text})
        answer = await openai_chat(self.history)
        self.history.append({"role": "assistant", "content": answer})

        wav_out = work_dir / "bot.wav"
        if settings.TTS_PROVIDER == "elevenlabs":
            await elevenlabs_tts(answer, wav_out)
        else:
            await openai_tts(answer, wav_out)
            
        if not wav_out.exists():
            return answer, None
            
        return answer, wav_out
