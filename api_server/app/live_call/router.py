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
