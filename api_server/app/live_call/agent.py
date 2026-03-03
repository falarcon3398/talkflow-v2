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
