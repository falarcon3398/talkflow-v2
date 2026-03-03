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
