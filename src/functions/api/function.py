from fastapi import FastAPI
from contextlib import asynccontextmanager
from loguru import logger
from mangum import Mangum
from typing import AsyncGenerator

from src.app import create_app, get_webhook_path
from src.settings import get_settings

cfg = get_settings()


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None]:
    logger.info("🚀 Starting application")
    from src.telegram.bot import start_telegram
    webhook_path = get_webhook_path(application)
    await start_telegram(webhook_path)
    yield
    logger.info("⛔ Stopping application")


# TODO: Try this pattern
# https://www.reddit.com/r/Python/comments/13g4ml1/do_you_use_singletons/

app = create_app(cfg, lifespan)
handler = Mangum(app, lifespan="on")