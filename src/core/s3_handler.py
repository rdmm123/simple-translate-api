import boto3
from typing import IO, Any
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

    def upload_file(self, file_path: Path, key: str) -> str:
        assert self.client
        logger.debug(f"Uploading file at {file_path} with key {key}")
        self.client.upload_file(str(file_path), self.bucket_name, key)
        return key

    def upload_file_obj(self, file_obj: IO[Any], key: str) -> str:
        assert self.client
        logger.debug(f"Uploading file_obj with key {key}")
        self.client.upload_fileobj(file_obj, self.bucket_name, key)
        return key


    def list_buckets(self) -> list[BucketTypeDef]:
        assert self.client
        response = self.client.list_buckets()
        logger.debug(response)
        return response['Buckets']