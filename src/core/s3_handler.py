import boto3
from pathlib import Path
from types_boto3_s3.client import S3Client
from typing import BinaryIO
from src.settings import get_settings

class S3Handler:
    _client: S3Client | None = None

    def __init__(self) -> None:
        settings = get_settings()
        self.bucket_name: str = settings.s3_bucket_name

    @classmethod
    def _get_client(cls) -> S3Client:
        if not cls._client:
            cls._client = boto3.client("s3")
        return cls._client

    def upload_file(self, file_path: Path) -> None:
        client = self._get_client()
        client.upload_file(str(file_path), self.bucket_name, str('videos' / file_path))

    def upload_file_obj(self, file_obj: BinaryIO) -> None:
        client = self._get_client()
        response = client.list_buckets()
        print(response)