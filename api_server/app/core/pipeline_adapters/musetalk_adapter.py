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
        final_output_path = self.output_dir / output_filename
        
        # In a real scenario, we would call the MuseTalk inference script here.
        # For Phase 1, we implement the caller logic that expects the environment to be ready.
        
        # Example command:
        # python3 -m musetalk.utils.inference --inference_config ... --result_dir ...
        
        logger.info(f"Running MuseTalk inference for job {job_id}")
        
        # Placeholder for actual subprocess call
        # result = subprocess.run([...], capture_output=True, text=True)
        
        # If inference fails or models are missing, we log and return None (to be handled by orchestrator)
        env_ok, _ = self.check_environment()
        if not env_ok:
            logger.error("Inference skipped: Environment not ready.")
            return None

        return str(final_output_path)

musetalk_adapter = MuseTalkAdapter()
