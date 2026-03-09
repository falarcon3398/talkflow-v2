from __future__ import annotations
import subprocess
import sys
from pathlib import Path
import time
import wave
import shutil
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
    """
    Create a static idle loop MP4 from a photo.
    Tries ffmpeg first (most reliable on macOS), then falls back to cv2.
    """
    idle_out.parent.mkdir(parents=True, exist_ok=True)

    # --- Strategy 1: ffmpeg (loop still image into video) ---
    ffmpeg_bin = shutil.which("ffmpeg")
    if ffmpeg_bin:
        try:
            cmd = [
                ffmpeg_bin,
                "-y",
                "-loop", "1",
                "-i", str(photo),
                "-c:v", "libx264",
                "-t", str(seconds),
                "-pix_fmt", "yuv420p",
                "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2",
                "-r", str(fps),
                str(idle_out),
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            if idle_out.exists() and idle_out.stat().st_size > 0:
                print(f"[IdleBuilder] Idle created via ffmpeg: {idle_out}")
                return
        except Exception as e:
            print(f"[IdleBuilder] ffmpeg failed: {e}, trying cv2 fallback")

    # --- Strategy 2: cv2 VideoWriter (mp4v) ---
    img = cv2.imread(str(photo))
    if img is None:
        raise RuntimeError(f"Could not read image {photo}")
    h, w = img.shape[:2]
    target_w = 1280
    scale = target_w / max(1, w)
    target_h = int(h * scale)
    img = cv2.resize(img, (target_w, target_h))
    if target_h < 720:
        pad = 720 - target_h
        img = cv2.copyMakeBorder(img, pad//2, pad - pad//2, 0, 0, cv2.BORDER_CONSTANT, value=(0,0,0))
    img = img[:720, :1280]

    # Try avc1 codec first (better macOS support), then mp4v
    for codec in ["avc1", "mp4v", "H264"]:
        try:
            fourcc = cv2.VideoWriter_fourcc(*codec)
            vw = cv2.VideoWriter(str(idle_out), fourcc, fps, (1280, 720))
            total = seconds * fps
            for _ in range(total):
                vw.write(img)
            vw.release()
            if idle_out.exists() and idle_out.stat().st_size > 1000:
                print(f"[IdleBuilder] Idle created via cv2 ({codec}): {idle_out}")
                return
            else:
                idle_out.unlink(missing_ok=True)
        except Exception:
            pass

    raise RuntimeError("Could not create idle.mp4 via ffmpeg or cv2. Install ffmpeg: brew install ffmpeg")

def build_idle_with_sadtalker(photo_path: Path, idle_out: Path, seconds: int | None = None) -> None:
    """
    Try SadTalker idle build. If it fails, fallback to static idle loop.
    """
    seconds = seconds or settings.IDLE_SECONDS
    idle_out.parent.mkdir(parents=True, exist_ok=True)

    tmp_dir = settings.OUTPUTS_DIR / "idle_tmp" / str(int(time.time()))
    tmp_dir.mkdir(parents=True, exist_ok=True)

    blank_wav = tmp_dir / "blank.wav"
    _make_blank_wav(blank_wav, seconds=max(2, min(5, seconds)))

    # Use sys.executable to avoid 'python not found' on macOS
    cmd = [
        sys.executable,
        settings.SADTALKER_PY,
        "--source_image", str(photo_path),
        "--driven_audio", str(blank_wav),
        "--result_dir", str(tmp_dir),
        "--device", settings.SADTALKER_DEVICE,
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        mp4s = list(tmp_dir.rglob("*.mp4"))
        if not mp4s:
            raise RuntimeError("SadTalker ran but no mp4 produced")
        mp4s.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        idle_out.write_bytes(mp4s[0].read_bytes())
        print(f"[IdleBuilder] Idle created via SadTalker: {idle_out}")
        return
    except Exception as e:
        print("[IdleBuilder] SadTalker failed, falling back to static idle loop:", e)
        _fallback_idle_from_image(photo_path, idle_out, seconds=seconds)

def lipsync_with_musetalk(face_video_or_image: Path, audio_wav: Path, out_mp4: Path) -> None:
    """
    MuseTalk lipsync for Live Call.
    Uses the configured MUSETALK_DIR and models.
    """
    import os
    import shutil
    import sys
    
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    if settings.LIPSYNC_MODE != "musetalk":
        raise RuntimeError(f"LIPSYNC_MODE is {settings.LIPSYNC_MODE}, not musetalk")

    musetalk_dir = Path(settings.MUSETALK_DIR)
    if not musetalk_dir.exists():
        raise RuntimeError(f"MuseTalk directory not found at {musetalk_dir}")

    # 1. Prepare Paths
    # We use the models from the root models directory
    # Based on our research, the models are in the models/musetalk/checkpoints/ directory
    project_root = Path(settings.MUSETALK_DIR).parent.parent
    checkpoints_root = project_root / "models" / "musetalk" / "checkpoints"
    
    # UNet v1.5
    unet_config = checkpoints_root / "musetalkV15" / "musetalk.json"
    unet_model = checkpoints_root / "musetalkV15" / "unet.pth"
    # VAE
    vae_path = checkpoints_root / "sd-vae-ft-mse"
    # Whisper
    whisper_dir = checkpoints_root / "whisper"
    
    # Task specific temp dir
    task_id = f"live_{int(time.time()*1000)}"
    temp_dir = out_mp4.parent / "musetalk_tmp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Create YAML config
    config_path = temp_dir / f"{task_id}.yaml"
    yaml_content = f"""
{task_id}:
  video_path: "{str(face_video_or_image)}"
  audio_path: "{str(audio_wav)}"
"""
    config_path.write_text(yaml_content)

    # Check if a .pkl file already exists in the same directory as the face image
    source_pkl = face_video_or_image.with_suffix(".pkl")
    use_saved = False
    if source_pkl.exists():
        # MuseTalk 1.5 expects the pkl at os.path.join(result_dir, "../", input_basename + ".pkl")
        # In our case, result_dir is temp_dir. So we copy it to temp_dir.parent
        target_pkl = temp_dir.parent / f"{face_video_or_image.stem}.pkl"
        shutil.copy(str(source_pkl), str(target_pkl))
        use_saved = True
        print(f"[LiveCall] Using pre-calculated landmarks from {source_pkl}", flush=True)

    # 3. Build Command
    vae_path = checkpoints_root / "sd-vae-ft-mse"
    cmd = [
        sys.executable, "scripts/inference.py",
        "--inference_config", str(config_path),
        "--result_dir", str(temp_dir),
        "--unet_config", str(unet_config),
        "--unet_model_path", str(unet_model),
        "--whisper_dir", str(whisper_dir),
        "--vae_type", str(vae_path),
        "--version", "v15",
        "--bbox_shift", "0"
    ]
    if use_saved:
        cmd.append("--use_saved_coord")

    print(f"[LiveCall] Running MuseTalk: {' '.join(cmd)}", flush=True)
    
    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{musetalk_dir}:{env.get('PYTHONPATH', '')}"
        
        result = subprocess.run(
            cmd, 
            cwd=str(musetalk_dir),
            capture_output=True, 
            text=True,
            check=False,
            env=env
        )
        
        if result.returncode != 0:
            print(f"[LiveCall] MuseTalk failed with code {result.returncode}")
            print(f"Stdout: {result.stdout}")
            print(f"Stderr: {result.stderr}")
            Path("/tmp/live_musetalk.log").write_text(f"Code: {result.returncode}\n\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}")
            raise RuntimeError(f"MuseTalk failed: {result.stderr}")
        else:
            print(f"[LiveCall] MuseTalk finished successfully.")
            print(f"Stdout: {result.stdout}")
            print(f"Stderr: {result.stderr}")
            Path("/tmp/live_musetalk_success.log").write_text(f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}")
        
        # 4. Find and move output
        # MuseTalk v15 puts results in {result_dir}/v15/
        generated = list(temp_dir.rglob("*.mp4"))
        if generated:
            # Sort by mtime to get the latest just in case
            generated.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            shutil.move(str(generated[0]), str(out_mp4))
            print(f"[LiveCall] MuseTalk success: {out_mp4}", flush=True)
        else:
            raise RuntimeError("MuseTalk ran but no video produced")
            
    finally:
        # Cleanup temp (Disabled for debug)
        if temp_dir.exists():
            # shutil.rmtree(temp_dir)
            pass

def lipsync_with_wav2lip(face_video_or_image: Path, audio_wav: Path, out_mp4: Path) -> None:
    """Legacy/Placeholder - user preferred MuseTalk"""
    raise RuntimeError("Wav2Lip not supported in this environment. Use MuseTalk.")
