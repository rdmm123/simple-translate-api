from fastapi import FastAPI
from fastapi.routing import APIRoute
from contextlib import asynccontextmanager
from loguru import logger
import src.telegram.handlers #noqa

from src.api.webhook import router, bot_webhook
from src.settings import get_settings

cfg = get_settings()

def get_webhook_path(application: FastAPI) -> str:
    func_name = bot_webhook.__name__

    try:
        webhook_route = [
            r for r in application.routes
            if r.name == func_name and isinstance(r, APIRoute)
        ][0]
    except IndexError:
        logger.error(f"Webhook path operation {func_name} not found. "
                     "Can't initialize application.")
        raise

    return webhook_route.path

@asynccontextmanager
async def lifespan(application: FastAPI):
    logger.info("🚀 Starting application")
    from src.telegram.bot import start_telegram
    webhook_path = get_webhook_path(application)
    await start_telegram(webhook_path)
    yield
    logger.info("⛔ Stopping application")

app = FastAPI(lifespan=lifespan)
app.include_router(router)