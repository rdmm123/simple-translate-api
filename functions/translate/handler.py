from typing import Any
from aws_lambda_typing.context import Context
from pydantic import ValidationError
from loguru import logger

from src.settings import get_settings
from src.lambda_events import TranslateVideoCommand
from src.video.translator import Translator
from src.misc.syncify import syncify

cfg = get_settings()


async def lambda_handler(event: dict[str, Any], context: Context) -> None:
    try:
        commmand = TranslateVideoCommand(**event)
    except ValidationError as e:
        logger.error(f"Invalid event received {e}")

    translator = Translator()
    await translator.translate(commmand.video_url, commmand.user_id)


handler = syncify(lambda_handler)
