import os
import time
import uuid
import glob
import pickle
import copy
import shutil
import subprocess
from argparse import Namespace

import gradio as gr
import spaces
import numpy as np
import cv2
import torch
import requests
import gdown
from tqdm import tqdm
from huggingface_hub import snapshot_download

from musetalk.utils.utils import get_file_type, get_video_fps, datagen, load_all_model
from musetalk.utils.preprocessing import get_landmark_and_bbox, read_imgs, coord_placeholder
from musetalk.utils.blending import get_image

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
CHECKPOINTS_DIR = os.path.join(PROJECT_DIR, "checkpoints")
RESULTS_DIR = os.path.join(PROJECT_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# -------- Model downloads (CPU) --------
def download_models_if_needed():
    # Simple sentinel: if MuseTalk weights folder exists, assume done
    if os.path.exists(os.path.join(CHECKPOINTS_DIR, "musetalk")):
        print("Models already present. Skipping download.")
        return

    os.makedirs(CHECKPOINTS_DIR, exist_ok=True)
    print("Downloading checkpoints...")

    t0 = time.time()

    # MuseTalk weights
    snapshot_download(
        repo_id="TMElyralab/MuseTalk",
        local_dir=CHECKPOINTS_DIR,
        max_workers=8,
        local_dir_use_symlinks=True,
    )

    # VAE weights
    snapshot_download(
        repo_id="stabilityai/sd-vae-ft-mse",
        local_dir=CHECKPOINTS_DIR,
        max_workers=8,
        local_dir_use_symlinks=True,
    )

    # DWPose weights
    snapshot_download(
        repo_id="yzd-v/DWPose",
        local_dir=CHECKPOINTS_DIR,
        max_workers=8,
        local_dir_use_symlinks=True,
    )

    # Whisper tiny
    whisper_dir = os.path.join(CHECKPOINTS_DIR, "whisper")
    os.makedirs(whisper_dir, exist_ok=True)
    whisper_path = os.path.join(whisper_dir, "tiny.pt")
    if not os.path.exists(whisper_path):
        url = "https://openaipublic.azureedge.net/main/whisper/models/65147644a518d12f04e32d6f3b26facc3f8dd46e5390956a9424a650c0ce22b9/tiny.pt"
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        with open(whisper_path, "wb") as f:
            f.write(r.content)

    # Face parsing weights (Google Drive)
    face_parse_dir = os.path.join(CHECKPOINTS_DIR, "face-parse-bisent")
    os.makedirs(face_parse_dir, exist_ok=True)
    face_parse_pth = os.path.join(face_parse_dir, "79999_iter.pth")
    if not os.path.exists(face_parse_pth):
        url = "https://drive.google.com/uc?id=154JgKpzCPW82qINcVieuPH3fZ2e0P812"
        gdown.download(url, face_parse_pth, quiet=False)

    # ResNet18
    resnet_path = os.path.join(face_parse_dir, "resnet18-5c106cde.pth")
    if not os.path.exists(resnet_path):
        url = "https://download.pytorch.org/models/resnet18-5c106cde.pth"
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        with open(resnet_path, "wb") as f:
            f.write(r.content)

    print(f"Download completed in {time.time() - t0:.1f}s")

download_models_if_needed()

# -------- Lazy model load (inside GPU call) --------
_MODELS = None

def get_models():
    global _MODELS
    if _MODELS is None:
        # Load after GPU is allocated (inside @spaces.GPU call)
        _MODELS = load_all_model()
    return _MODELS

def ffprobe_duration_seconds(path: str) -> float:
    # Returns duration in seconds using ffprobe
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        path
    ]
    out = subprocess.check_output(cmd).decode("utf-8").strip()
    return float(out)

def image_audio_to_ref_video(image_path: str, audio_path: str, fps: int = 25) -> str:
    job = uuid.uuid4().hex[:8]
    out_video = os.path.join(RESULTS_DIR, f"ref_{job}.mp4")

    # Create constant-frame-rate reference video from a single image + audio
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_path,
        "-i", audio_path,
        "-r", str(fps),
        "-shortest",
        "-vf", "format=yuv420p",
        "-c:v", "libx264",
        "-c:a", "aac", "-b:a", "192k",
        out_video
    ]
    subprocess.run(cmd, check=True)
    return out_video

@spaces.GPU(duration=600)
@torch.no_grad()
def inference(audio_path, video_path, bbox_shift, progress=gr.Progress(track_tqdm=True)):
    # Load models on first GPU call
    audio_processor, vae, unet, pe = get_models()

    args = Namespace(**{
        "result_dir": RESULTS_DIR,
        "fps": 25,
        "batch_size": 8,
        "output_vid_name": "",
        "use_saved_coord": False,
    })

    input_basename = os.path.basename(video_path).split(".")[0]
    audio_basename = os.path.basename(audio_path).split(".")[0]
    output_basename = f"{input_basename}_{audio_basename}"

    result_img_save_path = os.path.join(args.result_dir, output_basename)
    crop_coord_save_path = os.path.join(result_img_save_path, input_basename + ".pkl")

    os.makedirs(result_img_save_path, exist_ok=True)

    output_vid_name = os.path.join(args.result_dir, output_basename + ".mp4")

    # Extract frames from source video
    if get_file_type(video_path) == "video":
        save_dir_full = os.path.join(args.result_dir, input_basename)
        os.makedirs(save_dir_full, exist_ok=True)

        cmd = ["ffmpeg", "-v", "fatal", "-i", video_path, "-start_number", "0", f"{save_dir_full}/%08d.png"]
        subprocess.run(cmd, check=True)

        input_img_list = sorted(glob.glob(os.path.join(save_dir_full, "*.[jpJP][pnPN]*[gG]")))
        fps = get_video_fps(video_path)
    else:
        input_img_list = glob.glob(os.path.join(video_path, "*.[jpJP][pnPN]*[gG]"))
        input_img_list = sorted(input_img_list, key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))
        fps = args.fps

    # Audio features
    whisper_feature = audio_processor.audio2feat(audio_path)
    whisper_chunks = audio_processor.feature2chunks(feature_array=whisper_feature, fps=fps)

    # Landmarks & bbox
    if os.path.exists(crop_coord_save_path) and args.use_saved_coord:
        with open(crop_coord_save_path, "rb") as f:
            coord_list = pickle.load(f)
        frame_list = read_imgs(input_img_list)
    else:
        coord_list, frame_list = get_landmark_and_bbox(input_img_list, bbox_shift)
        with open(crop_coord_save_path, "wb") as f:
            pickle.dump(coord_list, f)

    # Latents
    input_latent_list = []
    for bbox, frame in zip(coord_list, frame_list):
        if bbox == coord_placeholder:
            continue
        x1, y1, x2, y2 = bbox
        crop_frame = frame[y1:y2, x1:x2]
        crop_frame = cv2.resize(crop_frame, (256, 256), interpolation=cv2.INTER_LANCZOS4)
        latents = vae.get_latents_for_unet(crop_frame)
        input_latent_list.append(latents)

    frame_list_cycle = frame_list + frame_list[::-1]
    coord_list_cycle = coord_list + coord_list[::-1]
    input_latent_list_cycle = input_latent_list + input_latent_list[::-1]

    # Inference
    video_num = len(whisper_chunks)
    batch_size = args.batch_size
    gen = datagen(whisper_chunks, input_latent_list_cycle, batch_size)

    device = unet.device if hasattr(unet, "device") else torch.device("cuda")
    timesteps = torch.tensor([0], device=device)

    res_frame_list = []
    for _, (whisper_batch, latent_batch) in enumerate(tqdm(gen, total=int(np.ceil(float(video_num) / batch_size)))):
        tensor_list = [torch.FloatTensor(arr) for arr in whisper_batch]
        audio_feature_batch = torch.stack(tensor_list).to(device)
        audio_feature_batch = pe(audio_feature_batch)

        pred_latents = unet.model(latent_batch, timesteps, encoder_hidden_states=audio_feature_batch).sample
        recon = vae.decode_latents(pred_latents)
        for res_frame in recon:
            res_frame_list.append(res_frame)

    # Blend back to full frames
    for i, res_frame in enumerate(tqdm(res_frame_list)):
        bbox = coord_list_cycle[i % len(coord_list_cycle)]
        ori_frame = copy.deepcopy(frame_list_cycle[i % len(frame_list_cycle)])
        x1, y1, x2, y2 = bbox
        try:
            res_frame = cv2.resize(res_frame.astype(np.uint8), (x2 - x1, y2 - y1))
        except Exception:
            continue
        combine_frame = get_image(ori_frame, res_frame, bbox)
        cv2.imwrite(f"{result_img_save_path}/{str(i).zfill(8)}.png", combine_frame)

    # Encode to mp4 + merge audio
    tmp_video = os.path.join(args.result_dir, f"tmp_{uuid.uuid4().hex[:8]}.mp4")
    cmd_img2video = [
        "ffmpeg", "-y", "-v", "fatal",
        "-r", str(fps),
        "-f", "image2",
        "-i", f"{result_img_save_path}/%08d.png",
        "-vcodec", "libx264",
        "-vf", "format=rgb24,scale=out_color_matrix=bt709,format=yuv420p",
        "-crf", "18",
        tmp_video
    ]
    subprocess.run(cmd_img2video, check=True)

    cmd_combine_audio = ["ffmpeg", "-y", "-v", "fatal", "-i", audio_path, "-i", tmp_video, output_vid_name]
    subprocess.run(cmd_combine_audio, check=True)

    # Cleanup
    try:
        os.remove(tmp_video)
    except Exception:
        pass
    shutil.rmtree(result_img_save_path, ignore_errors=True)

    return output_vid_name

def run(audio_path, ref_video_path, ref_image_path, bbox_shift):
    if not audio_path:
        raise gr.Error("Please upload an audio file.")

    # Prefer video if provided; else build reference video from image
    if ref_video_path:
        video_path = ref_video_path
    elif ref_image_path:
        video_path = image_audio_to_ref_video(ref_image_path, audio_path, fps=25)
    else:
        raise gr.Error("Please upload either a reference video OR a reference image.")

    return inference(audio_path, video_path, bbox_shift)

css = "#output_vid {max-width: 1024px; max-height: 576px}"

with gr.Blocks(css=css, title="1001 IBL Video Avatar — MuseTalk") as demo:
    gr.Markdown("## 1001 IBL Video Avatar — MuseTalk (ZeroGPU)\nUpload **Audio + Video** (best) or **Audio + Image**.")

    with gr.Row():
        audio = gr.Audio(label="Driven Audio", type="filepath")
        video = gr.Video(label="Reference Video (optional)")
        image = gr.Image(label="Reference Image (optional)", type="filepath")

    bbox_shift = gr.Slider(label="BBox shift", minimum=-9, maximum=9, value=-1, step=1)
    btn = gr.Button("Generate (MuseTalk)")
    out = gr.Video(label="Output", elem_id="output_vid")

    btn.click(fn=run, inputs=[audio, video, image, bbox_shift], outputs=[out])

demo.queue().launch(share=False, debug=True, server_name="0.0.0.0", server_port=7860, ssr_mode=False)
