from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import final, Literal

@final
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')
    debug: bool = True
    telegram_token: str = '1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    base_webhook_url: str = 'https://my.host.name'
    webhook_auth_token: str = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'  # Additional security token for webhook
    web_user: str = 'user'
    web_pass: str = 'pass'
    runtime: Literal['server', 'lambda'] = 'server'
    environment: Literal['dev', 'prd'] = 'dev'
    s3_bucket_name: str = 'bucket-name'


@lru_cache()  # get it from memory
def get_settings() -> Settings:
    return Settings()
