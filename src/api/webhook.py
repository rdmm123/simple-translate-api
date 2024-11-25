from fastapi import APIRouter, Header, Depends, HTTPException, status
from typing import Annotated
from aiogram.types import Update
from aiogram import Bot, Dispatcher
from loguru import logger

from src.settings import get_settings
from src.telegram.bot import get_bot, get_dispatcher

router = APIRouter(tags=["webhook"], prefix="/webhook")
cfg =  get_settings()

async def validate_webhook(
    x_telegram_bot_api_secret_token: Annotated[str, Header()]
) -> bool:
    # TODO: Verify IP is from telegram -> 149.154.160.0/20 and 91.108.4.0/22
    if x_telegram_bot_api_secret_token != cfg.webhook_auth_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")


@router.post('/', dependencies=[Depends(validate_webhook)])
async def bot_webhook(
    update: dict,
    bot: Annotated[Bot, Depends(get_bot)],
    dp: Annotated[Dispatcher, Depends(get_dispatcher)]
) -> None | dict:
    """ Register webhook endpoint for telegram bot"""
    telegram_update = Update(**update)
    await dp.feed_webhook_update(bot=bot, update=telegram_update)