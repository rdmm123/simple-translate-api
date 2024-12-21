import boto3

from pathlib import Path
from types_boto3_s3.client import S3Client
from types_boto3_s3.type_defs import BucketTypeDef

from src.settings import get_settings

from loguru import logger

class S3Handler:
    client: S3Client | None = None

    def __init__(self) -> None:
        settings = get_settings()
        self.bucket_name: str = settings.s3_bucket_name
        self.client = self._get_client()

    @classmethod
    def _get_client(cls) -> S3Client:
        if not cls.client:
            cls.client = boto3.client("s3")
        return cls.client

    def upload_file(self, file_path: Path) -> None:
        assert self.client
        self.client.upload_file(
            str(file_path), self.bucket_name, str("videos" / file_path)
        )

    def list_buckets(self) -> list[BucketTypeDef]:
        assert self.client
        response = self.client.list_buckets()
        logger.debug(response)
        return response['Buckets']