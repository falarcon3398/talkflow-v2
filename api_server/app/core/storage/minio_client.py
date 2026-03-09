from minio import Minio
from app.config import settings
import io
import os

class MinioClient:
    def __init__(self):
        try:
            self.client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE
            )
            self._ensure_bucket()
            print(f"MinioClient initialized on {settings.MINIO_ENDPOINT}")
        except Exception as e:
            print(f"FAILED to initialize Minio: {e}")
            self.client = None

    def _ensure_bucket(self):
        if self.client and not self.client.bucket_exists(settings.MINIO_BUCKET):
            self.client.make_bucket(settings.MINIO_BUCKET)

    def upload_file(self, file_path: str, object_name: str):
        if not self.client:
            print(f"WARNNING: Storage not configured. Skipping upload of {object_name}")
            return object_name
        
        self.client.fput_object(
            settings.MINIO_BUCKET,
            object_name,
            file_path
        )
        return object_name

    def download_file(self, object_name: str, file_path: str):
        if not self.client:
            print(f"WARNNING: Storage not configured. Cannot download {object_name}")
            return
            
        # Ensure local directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        self.client.fget_object(
            settings.MINIO_BUCKET,
            object_name,
            file_path
        )

minio_client = MinioClient()
