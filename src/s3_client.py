import boto3
from pathlib import Path
from botocore.client import BaseClient
from typing import BinaryIO
from src.settings import get_settings

class S3Client:
    _client: BaseClient | None = None

    def __init__(self):
        settings = get_settings()
        self.bucket_name: str = settings.s3_bucket_name

    @classmethod
    def _get_client(cls) -> BaseClient:
        if not cls._client:
            cls._client = boto3.client("s3")
        return cls._client

    def upload_file(self, file_path: Path) -> bool:
        client = self._get_client()
        response = client.upload_file(str(file_path), self.bucket_name, 'video')
        print(response)
        return True

    def upload_file_obj(self, file_obj: BinaryIO):
        client = self._get_client()
        response = client.list_buckets()
        print(response)