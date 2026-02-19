from minio import Minio
from app.config import settings
import io

class MinioClient:
    def __init__(self):
        # Stubbed for local development
        self.client = None
        print("MinioClient initialized in STUB mode (local development)")

    def _ensure_bucket(self):
        pass

    def upload_file(self, file_path: str, object_name: str):
        print(f"STUB: Uploading {file_path} as {object_name}")
        return object_name

    def download_file(self, object_name: str, file_path: str):
        print(f"STUB: Downloading {object_name} to {file_path}")

minio_client = MinioClient()
