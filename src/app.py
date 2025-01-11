import boto3
from fastapi import FastAPI
from starlette.types import Lifespan
from fastapi.routing import APIRoute
from src.settings import Settings
from loguru import logger

from src.api import (
    webhook,
    health
)


def create_app(
    settings: Settings,
    lifespan: Lifespan[FastAPI] | None = None,
    include_dev_routes: bool = True
) -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(webhook.router)
    app.include_router(health.router)

    if settings.environment == 'dev':
        if include_dev_routes:
            from src.api import dev
            app.include_router(dev.router)
        boto3.set_stream_logger('')

    return app


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
