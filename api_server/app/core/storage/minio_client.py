from minio import Minio
from app.config import settings
import io

class MinioClient:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self._ensure_bucket()

    def _ensure_bucket(self):
        if not self.client.bucket_exists(settings.MINIO_BUCKET):
            self.client.make_bucket(settings.MINIO_BUCKET)

    def upload_file(self, file_path: str, object_name: str):
        self.client.fput_object(settings.MINIO_BUCKET, object_name, file_path)
        return object_name

    def download_file(self, object_name: str, file_path: str):
        self.client.fget_object(settings.MINIO_BUCKET, object_name, file_path)

minio_client = MinioClient()
