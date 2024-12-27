import boto3
from fastapi import FastAPI
from fastapi.routing import APIRoute
from contextlib import asynccontextmanager
from loguru import logger
from typing import AsyncGenerator

from src.api import (
    webhook,
    dev,
    health
)
from src.core.scraper import Scraper
from src.settings import get_settings

cfg = get_settings()

def get_webhook_path(application: FastAPI) -> str:
    func_name = webhook.bot_webhook.__name__

    try:
        webhook_route = [
            r for r in application.routes
            if isinstance(r, APIRoute) and r.name == func_name
        ][0]
    except IndexError:
        logger.error(f"Webhook path operation {func_name} not found. "
                     "Can't initialize application.")
        raise

    return webhook_route.path

@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None]:
    logger.info("🚀 Starting application")
    from src.telegram.bot import start_telegram
    webhook_path = get_webhook_path(application)
    scraper = await Scraper.create()
    await start_telegram(webhook_path)
    yield
    await scraper.close()
    logger.info("⛔ Stopping application")

# TODO: Try this pattern
# https://www.reddit.com/r/Python/comments/13g4ml1/do_you_use_singletons/

app = FastAPI(lifespan=lifespan)
app.include_router(webhook.router)
app.include_router(health.router)

if cfg.environment == 'dev':
    app.include_router(dev.router)
    boto3.set_stream_logger('')

if cfg.runtime == 'lambda':
    from mangum import Mangum
    handler = Mangum(app, lifespan="on")