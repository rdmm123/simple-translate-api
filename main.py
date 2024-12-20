from fastapi import FastAPI
from fastapi.routing import APIRoute
from contextlib import asynccontextmanager
from loguru import logger
from typing import AsyncGenerator

from src.api.webhook import router as wh_router, bot_webhook
from src.api.dev import router as dev_router
from src.core.scraper import Scraper
from src.settings import get_settings

cfg = get_settings()

def get_webhook_path(application: FastAPI) -> str:
    func_name = bot_webhook.__name__

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

app = FastAPI(lifespan=lifespan)
app.include_router(wh_router)

if cfg.environment == 'dev':
    app.include_router(dev_router)