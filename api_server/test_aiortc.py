import asyncio
from aiortc import RTCPeerConnection, MediaStreamTrack
import inspect

class DummyTrack(MediaStreamTrack):
    kind = "audio"
    async def recv(self):
        pass

async def check():
    pc = RTCPeerConnection()
    track = DummyTrack()
    trans = pc.addTransceiver("audio")
    res = trans.sender.replaceTrack(track)
    print(f"replaceTrack result: {res}")
    print(f"is coroutine: {inspect.iscoroutine(res)}")
    print(f"is coroutine function: {inspect.iscoroutinefunction(trans.sender.replaceTrack)}")
    await pc.close()

asyncio.run(check())
