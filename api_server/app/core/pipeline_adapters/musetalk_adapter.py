import subprocess
import os
from pathlib import Path
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class MuseTalkAdapter:
    def __init__(self):
        self.base_dir = Path(settings.BASE_DIR)
        self.models_dir = Path(settings.MODELS_PATH)
        self.output_dir = Path(settings.OUTPUT_DIR)
        self.scripts_dir = self.base_dir / "scripts" / "musetalk"
        
    def check_environment(self):
        """Verifies if the necessary models and scripts exist."""
        required_models = [
            "musetalk/checkpoints/musetalk/musetalk.json",
            "musetalk/checkpoints/musetalk/pytorch_model.bin",
            "musetalk/checkpoints/dwpose/dw-ll_ucoco_384.onnx",
            "musetalk/checkpoints/face-parse-bisent/79999_iter.pth",
            "musetalk/checkpoints/sd-vae-ft-mse/diffusion_pytorch_model.bin"
        ]
        
        missing = []
        for model in required_models:
            if not (self.models_dir / model).exists():
                missing.append(model)
        
        if missing:
            logger.warning(f"Missing MuseTalk models: {', '.join(missing)}")
            return False, missing
        return True, []

    def run_inference(self, avatar_path: str, audio_path: str, job_id: str) -> str:
        """
        Runs the MuseTalk inference via subprocess.
        Returns the path to the generated video.
        """
        output_filename = f"{job_id}_musetalk.mp4"
        musetalk_dir = Path(settings.MUSETALK_DIR)
        
        if not musetalk_dir.exists():
            logger.error(f"MuseTalk directory not found at {musetalk_dir}")
            return None

        # 1. Create temporary inference config
        # The script scripts/inference.py reads a YAML with task_id: {video_path, audio_path}
        temp_config_path = musetalk_dir / "configs" / "inference" / f"job_{job_id}.yaml"
        temp_config_path.parent.mkdir(parents=True, exist_ok=True)
        
        yaml_content = f"""
job_{job_id}:
  video_path: "{avatar_path}"
  audio_path: "{audio_path}"
"""
        temp_config_path.write_text(yaml_content)
        
        # 2. Prepare paths
        # We use the corrected MODELS_PATH which points to the root models/
        unet_config = self.models_dir / "musetalk" / "checkpoints" / "musetalk" / "musetalk.json"
        unet_model = self.models_dir / "musetalk" / "checkpoints" / "musetalk" / "pytorch_model.bin"
        whisper_dir = "openai/whisper-tiny"
        vae_dir = self.models_dir / "musetalk" / "checkpoints" / "sd-vae-ft-mse"
        resnet_path = self.models_dir / "musetalk" / "checkpoints" / "face-parse-bisent" / "resnet18-5c106cde.pth"
        face_parsing_model_path = self.models_dir / "musetalk" / "checkpoints" / "face-parse-bisent" / "79999_iter.pth"
        result_dir = self.output_dir / job_id
        result_dir.mkdir(parents=True, exist_ok=True)

        env_ok, _ = self.check_environment()
        if not env_ok:
            logger.error("Inference skipped: Environment not ready.")
            return None

        # 3. Construct command
        # MuseTalk 1.5 expects weights via CLI and tasks via YAML
        import sys
        cmd = [
            sys.executable, "scripts/inference.py",
            "--inference_config", str(temp_config_path),
            "--result_dir", str(result_dir),
            "--unet_config", str(unet_config),
            "--unet_model_path", str(unet_model),
            "--whisper_dir", whisper_dir,
            "--vae_type", str(vae_dir),
            "--resnet_path", str(resnet_path),
            "--face_parsing_model_path", str(face_parsing_model_path),
            "--bbox_shift", "0"
        ]
        
        logger.info(f"Executing MuseTalk: {' '.join(cmd)}")
        
        try:
            # Set PYTHONPATH so internal musetalk package is findable
            env = os.environ.copy()
            env["PYTHONPATH"] = f"{musetalk_dir}:{env.get('PYTHONPATH', '')}"
            
            result = subprocess.run(
                cmd, 
                cwd=str(musetalk_dir),
                capture_output=True, 
                text=True,
                check=False,  # Don't throw yet, we want to log outputs
                env=env
            )
            
            if result.stdout:
                logger.info(f"MuseTalk Stdout: {result.stdout}")
            if result.stderr:
                logger.warning(f"MuseTalk Stderr: {result.stderr}")

            if result.returncode != 0:
                logger.error(f"MuseTalk inference failed with exit code {result.returncode}")
                return None

            logger.info("MuseTalk inference completed successfully. Checking for outputs...")
            
            # 4. Handle output
            # List all files for debugging
            all_files = list(result_dir.rglob("*"))
            logger.info(f"Files found in {result_dir}: {[str(f.relative_to(result_dir)) for f in all_files]}")

            generated_files = list(result_dir.rglob("*.mp4"))
            if generated_files:
                # Sort by size or modification time to get the most likely actual video if multiple exist
                generated_files.sort(key=lambda x: x.stat().st_size, reverse=True)
                final_output_path = self.output_dir / output_filename
                import shutil
                shutil.move(str(generated_files[0]), str(final_output_path))
                logger.info(f"Successfully moved {generated_files[0]} to {final_output_path}")
                
                # Cleanup
                if temp_config_path.exists():
                    temp_config_path.unlink()
                
                return str(final_output_path)
            else:
                logger.error(f"MuseTalk finished but no MP4 found in {result_dir}")
                return None
                
        except Exception as e:
            logger.error(f"Unexpected error during MuseTalk inference: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None

musetalk_adapter = MuseTalkAdapter()
