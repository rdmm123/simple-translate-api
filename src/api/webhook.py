from typing import Annotated

from aiogram import Bot, Dispatcher
from aiogram.types import Update
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Header,
    HTTPException,
    status,
)

from src.dependencies import SettingsDep, BotDep, DispatcherDep


router = APIRouter(tags=["webhook"], prefix="/webhook")


async def validate_webhook(
    settings: SettingsDep, x_telegram_bot_api_secret_token: Annotated[str, Header()]
) -> None:
    # TODO: Verify IP is from telegram -> 149.154.160.0/20 and 91.108.4.0/22
    if x_telegram_bot_api_secret_token != settings.webhook_auth_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")


async def send_webhook_update(update: Update, bot: Bot, dp: Dispatcher) -> None:
    await dp.feed_webhook_update(bot=bot, update=update)


@router.post("", dependencies=[Depends(validate_webhook)])
async def bot_webhook(
    update: Update,
    backgrund_tasks: BackgroundTasks,
    bot: BotDep,
    dp: DispatcherDep,
) -> None:
    # Use background task to not delay response
    backgrund_tasks.add_task(send_webhook_update, update, bot, dp)
    return None