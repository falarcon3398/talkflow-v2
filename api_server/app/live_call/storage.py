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
