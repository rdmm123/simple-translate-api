from loguru import logger
from pydantic import BaseModel, HttpUrl
from enum import Enum

from src.core.helpers import validate_url
from src.settings import get_settings

class Action(Enum):
    REPLY_WITH_MESSAGE = 1
    REPLY_WITH_VIDEO = 2
    TRANSLATE_VIDEO = 3
    TRIGGER_TRANSLATION_LAMBDA = 4

class Result(BaseModel):
    action: Action
    value: str | HttpUrl | None

class Evaluator:
    def __init__(self) -> None:
        self._settings = get_settings()

    def _get_video_from_bucket(self, video_id: str) -> None:
        # TODO: implement this
        return None

    def evaluate(self, url: str, user_id: str) -> Result:
        """Evaluate the current situation and return the action to take"""
        if not (url_obj := validate_url(url)):
            # TODO: send telegram message indicating that url isn't valid
            logger.warning(f"Invalid url received {url}")
            return Result(action=Action.REPLY_WITH_MESSAGE, value="Url is not valid")

        if (self._get_video_from_bucket("fake_video_id")): # type: ignore
            return Result(action=Action.REPLY_WITH_VIDEO, value="fake_video_url")

        if self._settings.runtime == 'lambda':
            return Result(action=Action.TRIGGER_TRANSLATION_LAMBDA, value=url_obj)

        return Result(action=Action.TRANSLATE_VIDEO, value=url_obj)
