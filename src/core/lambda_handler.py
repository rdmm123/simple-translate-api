import boto3
from types_boto3_lambda import LambdaClient
from types_boto3_lambda.type_defs import InvocationResponseTypeDef
from pydantic import BaseModel

from src.settings import get_settings


class LambdaHandler:
    client: LambdaClient | None = None

    def __init__(self) -> None:
        self._settings = get_settings()
        self.client = self._get_client()

    @classmethod
    def _get_client(cls, host: str | None = None) -> LambdaClient:
        if not cls.client:
            cls.client = boto3.client("lambda", endpoint_url=host)
        return cls.client

    def invoke_async(
        self, func_name: str, event: BaseModel
    ) -> InvocationResponseTypeDef:
        assert self.client
        return self.client.invoke(
            FunctionName=func_name,
            InvocationType="Event",
            Payload=event.model_dump_json(),
        )

    def invoke_sync(
        self, func_name: str, event: BaseModel
    ) -> InvocationResponseTypeDef:
        assert self.client
        return self.client.invoke(
            FunctionName=func_name,
            InvocationType="RequestResponse",
            Payload=event.model_dump_json(),
        )
