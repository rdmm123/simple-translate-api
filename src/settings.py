from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import final, Annotated
from fastapi import Depends


@final
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')
    debug: bool = True
    telegram_token: str = '1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    base_webhook_url: str = 'https://my.host.name'
    webhook_auth_token: str = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'  # Additional security token for webhook
    web_user: str = 'user'
    web_pass: str = 'pass'


@lru_cache()  # get it from memory
def get_settings() -> Settings:
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]