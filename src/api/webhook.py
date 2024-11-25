from fastapi import APIRouter, Header
from typing import Annotated
from loguru import logger
from aiogram.types import Update

from src.settings import get_settings
from src.telegram.bot import bot, dp

router = APIRouter(tags=["webhook"], prefix="/webhook")
cfg =  get_settings()

@router.get("/")
async def root() -> dict:
    return {"message": "Hello World"}


@router.post('/')
async def bot_webhook(
        update: dict,
        x_telegram_bot_api_secret_token: Annotated[str | None, Header()] = None) -> None | dict:
    """ Register webhook endpoint for telegram bot"""
    if x_telegram_bot_api_secret_token != cfg.webhook_auth_token:
        logger.error("Wrong secret token !")
        return {"status": "error", "mes sage": "Wrong secret token !"}
    telegram_update = Update(**update)
    logger.debug(telegram_update)
    await dp.feed_webhook_update(bot=bot, update=telegram_update)