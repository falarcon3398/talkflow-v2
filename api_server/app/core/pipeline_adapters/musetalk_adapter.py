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
            "musetalk/musetalk.json",
            "musetalk/pytorch_model.bin",
            "dwpose/dw-ll_ucoco_384.onnx",
            "face-parse-bisent/79999_iter.pth",
            "sd-vae-ft-mse/diffusion_pytorch_model.bin"
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
        # MuseTalk usually outputs to a results folder within its own directory
        # We will move it to our output_dir afterwards
        temp_result_dir = self.output_dir / job_id
        temp_result_dir.mkdir(parents=True, exist_ok=True)
        
        env_ok, _ = self.check_environment()
        if not env_ok:
            logger.error("Inference skipped: Environment not ready.")
            return None

        # MuseTalk standard command line
        # Use -m to run as a module if possible, or direct python script
        cmd = [
            "python3", "-m", "musetalk.utils.inference",
            "--inference_config", str(self.scripts_dir / "inference_config.yaml"),
            "--bbox_shift", "0",
            "--result_dir", str(temp_result_dir),
            "--video_path", str(avatar_path),
            "--audio_path", str(audio_path)
        ]
        
        logger.info(f"Executing MuseTalk: {' '.join(cmd)}")
        
        try:
            # Change working directory to MUSETALK_DIR to ensure relative imports work inside their codebase
            musetalk_dir = Path(settings.MUSETALK_DIR)
            result = subprocess.run(
                cmd, 
                cwd=str(musetalk_dir) if musetalk_dir.exists() else None,
                capture_output=True, 
                text=True,
                check=True
            )
            logger.info("MuseTalk inference completed successfully.")
            
            # Find the output file (MuseTalk names it based on input names usually)
            # For now, we assume it's the only mp4 in that result dir
            generated_files = list(temp_result_dir.glob("*.mp4"))
            if generated_files:
                final_output_path = self.output_dir / output_filename
                import shutil
                shutil.move(str(generated_files[0]), str(final_output_path))
                return str(final_output_path)
            else:
                logger.error("MuseTalk finished but no MP4 found in result directory.")
                return None
                
        except subprocess.CalledProcessError as e:
            logger.error(f"MuseTalk inference failed with exit code {e.returncode}")
            logger.error(f"Stderr: {e.stderr}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during MuseTalk inference: {str(e)}")
            return None

musetalk_adapter = MuseTalkAdapter()
