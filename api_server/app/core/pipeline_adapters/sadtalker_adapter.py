import subprocess
import os
import shutil
from pathlib import Path
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class SadTalkerAdapter:
    def __init__(self):
        self.sadtalker_dir = Path(settings.SADTALKER_DIR) if settings.SADTALKER_DIR else None
        self.venv_python = Path(settings.SADTALKER_VENV_PYTHON) if settings.SADTALKER_VENV_PYTHON else None
        self.output_dir = Path(settings.OUTPUT_DIR) if settings.OUTPUT_DIR else None
        
    def check_environment(self):
        """Verifies if SadTalker environment is ready."""
        if not self.sadtalker_dir.exists():
            return False, ["SadTalker directory missing"]
        if not self.venv_python.exists():
            return False, ["SadTalker venv python missing"]
        return True, []

    def run_inference(self, avatar_path: str, audio_path: str, job_id: str) -> str:
        """
        Runs SadTalker inference via CLI and parses progress.
        Returns the path to the generated video.
        """
        from app.core.pipeline.orchestrator import update_job_status
        import re

        output_filename = f"{job_id}_sadtalker.mp4"
        result_dir = Path(settings.PROCESSING_DIR) / job_id
        result_dir.mkdir(parents=True, exist_ok=True)

        env_ok, errors = self.check_environment()
        if not env_ok:
            logger.error(f"SadTalker environment check failed: {errors}")
            return None

        # Construct command
        cmd = [
            str(self.venv_python),
            str(self.sadtalker_dir / "inference.py"),
            "--source_image", os.path.abspath(str(avatar_path)),
            "--driven_audio", os.path.abspath(str(audio_path)),
            "--result_dir", os.path.abspath(str(result_dir)),
            "--still",
            "--preprocess", "crop",
            "--enhancer", "gfpgan",
            "--cpu"
        ]
        
        logger.info(f"Executing SadTalker: {' '.join(cmd)}")
        
        try:
            # We use Popen to capture progress in real-time
            process = subprocess.Popen(
                cmd,
                cwd=str(self.sadtalker_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, # SadTalker/tqdm usually writes to stderr
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Regex to match [34/635] style progress
            progress_regex = re.compile(r"\[(\d+)/(\d+)\]")

            for line in process.stdout:
                # Log everything to debug log
                # logger.debug(f"[SADTALKER] {line.strip()}")
                
                match = progress_regex.search(line)
                if match:
                    current = int(match.group(1))
                    total = int(match.group(2))
                    # Map [30-70%] progress range for lipsync step
                    percentage = 30 + int((current / total) * 40)
                    update_job_status(job_id, progress=percentage)

            process.wait()
            
            if process.returncode != 0:
                logger.error(f"SadTalker inference failed with exit code {process.returncode}")
                return None

            logger.info("SadTalker inference completed successfully.")
            
            generated_files = list(result_dir.rglob("*.mp4"))
            if generated_files:
                enhanced_files = [f for f in generated_files if "_enhanced" in f.name]
                source_file = enhanced_files[0] if enhanced_files else generated_files[0]
                
                final_output_path = self.output_dir / output_filename
                shutil.copy(str(source_file), str(final_output_path))
                
                logger.info(f"Final video moved to {final_output_path}")
                return str(final_output_path)
            else:
                logger.error(f"SadTalker finished but no MP4 found in {result_dir}")
                return None
                
        except Exception as e:
            logger.error(f"Unexpected error during SadTalker inference: {str(e)}")
            return None

sadtalker_adapter = SadTalkerAdapter()
