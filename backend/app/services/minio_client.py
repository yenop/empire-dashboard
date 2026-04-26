from minio import Minio
from minio.error import S3Error

from app.config import get_settings


def ensure_bucket() -> bool:
    settings = get_settings()
    client = Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
    )
    try:
        if not client.bucket_exists(settings.minio_bucket):
            client.make_bucket(settings.minio_bucket)
        return True
    except S3Error:
        return False
