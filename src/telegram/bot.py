from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import WebhookInfo, BotCommand
from aiogram.client.default import DefaultBotProperties
from functools import lru_cache

from loguru import logger

from src.settings import get_settings, Settings
from src.telegram.handlers import router

cfg: Settings = get_settings()


@lru_cache()
def get_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.include_router(router)
    return dp


@lru_cache
def get_bot() -> Bot:
    return Bot(
        token=cfg.telegram_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )


async def set_webhook(my_bot: Bot, webhook_path: str) -> None:
    # Check and set webhook for Telegram
    async def check_webhook() -> WebhookInfo | None:
        try:
            webhook_info = await my_bot.get_webhook_info()
            return webhook_info
        except Exception as e:
            logger.error(f"Can't get webhook info - {e}")
            return None

    current_webhook_info = await check_webhook()
    webhook_url =f"{cfg.base_webhook_url}{webhook_path}"

    if cfg.debug:
        logger.debug(f"Current bot info: {current_webhook_info}")

    if not current_webhook_info:
        return

    if webhook_url == current_webhook_info.url:
        return

    try:
        await my_bot.set_webhook(
            webhook_url,
            secret_token=cfg.webhook_auth_token,
            drop_pending_updates=current_webhook_info.pending_update_count > 0,
            max_connections=40 if cfg.debug else 100,
        )
        if cfg.debug:
            logger.debug(f"Updated bot info: {await check_webhook()}")
    except Exception as e:
        logger.error(f"Can't set webhook - {e}")


async def set_bot_commands_menu(my_bot: Bot) -> None:
    # Register commands for Telegram bot (menu)
    commands = [
        BotCommand(command="/translate", description="Translate video from url"),
    ]
    try:
        await my_bot.set_my_commands(commands)
    except Exception as e:
        logger.error(f"Can't set commands - {e}")


async def start_telegram(webwook_path: str | None = None) -> None:
    bot = get_bot()
    get_dispatcher()

    if webwook_path:
        await set_webhook(bot, webwook_path)
        await set_bot_commands_menu(bot)