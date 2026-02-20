import os
import sys
import torch
import spaces
import gradio as gr
import shutil
from pathlib import Path
from huggingface_hub import snapshot_download

# --- Path Setup ---
ROOT_DIR = Path(__file__).parent.absolute()
MUSETALK_DIR = ROOT_DIR / "api_server" / "musetalk"
sys.path.append(str(MUSETALK_DIR))

# --- Model Downloads ---
def download_models():
    models_root = ROOT_DIR / "models"
    # We check for a vital file to avoid re-downloading
    if (models_root / "musetalkV15" / "unet.pth").exists():
        print("Models already exist.")
        return
    
    print("Downloading weights from Hugging Face...")
    # MuseTalk Weights (V1.0 and V1.5)
    snapshot_download(
        repo_id="TMElyralab/MuseTalk",
        local_dir=str(models_root),
        allow_patterns=["musetalk/*", "musetalkV15/*"]
    )
    # SD VAE
    snapshot_download(
        repo_id="stabilityai/sd-vae-ft-mse",
        local_dir=str(models_root / "sd-vae"),
        allow_patterns=["config.json", "diffusion_pytorch_model.bin"]
    )
    # Whisper Tiny
    snapshot_download(
        repo_id="openai/whisper-tiny",
        local_dir=str(models_root / "whisper"),
        allow_patterns=["config.json", "pytorch_model.bin", "preprocessor_config.json"]
    )
    # DWPose
    snapshot_download(
        repo_id="yzd-v/DWPose",
        local_dir=str(models_root / "dwpose"),
        allow_patterns=["dw-ll_ucoco_384.pth"]
    )
    # Face Parsing
    snapshot_download(
        repo_id="pwwu/face-parse-bisent",
        local_dir=str(models_root / "face-parse-bisent")
    )
    print("Weights downloaded successfully.")

# Startup download
download_models()

# --- MuseTalk Imports ---
from scripts.inference import main as musetalk_inference

class Args:
    def __init__(self):
        self.ffmpeg_path = "ffmpeg"
        self.gpu_id = 0
        self.vae_type = "sd-vae"
        self.unet_config = str(ROOT_DIR / "models" / "musetalkV15" / "musetalk.json")
        self.unet_model_path = str(ROOT_DIR / "models" / "musetalkV15" / "unet.pth")
        self.whisper_dir = str(ROOT_DIR / "models" / "whisper")
        self.inference_config = ""
        self.bbox_shift = 0
        self.result_dir = str(ROOT_DIR / "results")
        self.extra_margin = 10
        self.fps = 25
        self.audio_padding_length_left = 2
        self.audio_padding_length_right = 2
        self.batch_size = 4 # Reduced for ZeroGPU stability
        self.output_vid_name = None
        self.use_saved_coord = False
        self.saved_coord = False
        self.use_float16 = True
        self.parsing_mode = 'jaw'
        self.left_cheek_width = 90
        self.right_cheek_width = 90
        self.version = "v15"

@spaces.GPU(duration=180)
def generate_lipsync(image_path, audio_path, bbox_shift):
    if image_path is None or audio_path is None:
        return None
    
    # Create temporary inference config
    job_id = "gradio_job"
    temp_dir = ROOT_DIR / "temp_configs"
    temp_dir.mkdir(exist_ok=True)
    conf_path = temp_dir / f"{job_id}.yaml"
    
    with open(conf_path, "w") as f:
        f.write(f"{job_id}:\n")
        f.write(f"  video_path: \"{image_path}\"\n")
        f.write(f"  audio_path: \"{audio_path}\"\n")
        f.write(f"  bbox_shift: {bbox_shift}\n")

    args = Args()
    args.inference_config = str(conf_path)
    args.bbox_shift = bbox_shift
    
    # Run inference
    try:
        musetalk_inference(args)
        
        # Look for output
        out_root = Path(args.result_dir) / args.version
        # Get the latest mp4 in that dir
        generated_files = sorted(list(out_root.glob("*.mp4")), key=os.path.getmtime)
        
        if generated_files:
            return str(generated_files[-1])
        return None
    except Exception as e:
        print(f"Inference Error: {e}")
        return None
    finally:
        if conf_path.exists():
            conf_path.unlink()

# --- UI ---
with gr.Blocks(title="TalkFlow - MuseTalk LipSync") as demo:
    gr.Markdown("# 🎬 TalkFlow: MuseTalk 1.5 Hub")
    gr.Markdown("ZeroGPU-powered Lipsync. Upload avatar (img/video) and audio.")
    
    with gr.Row():
        with gr.Column():
            input_img = gr.Image(label="Avatar Image/Video", type="filepath")
            input_audio = gr.Audio(label="Audio", type="filepath")
            bbox_shift = gr.Slider(minimum=-20, maximum=20, value=0, label="BBox Shift")
            btn = gr.Button("Generate LipSync", variant="primary")
        
        with gr.Column():
            output_video = gr.Video(label="Result")
            
    btn.click(
        fn=generate_lipsync,
        inputs=[input_img, input_audio, bbox_shift],
        outputs=output_video
    )

if __name__ == "__main__":
    demo.launch()
