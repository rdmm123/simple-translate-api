from aiogram import types
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.utils.markdown import hbold
from aiogram.types import Message

from loguru import logger
from pydantic import HttpUrl
from src.video.evaluator import Evaluator, Action

router = Router(name=__name__)


@router.message(Command("translate"))
async def cmd_id(message: Message) -> None:
    await message.answer("Envia la URL del video a traducir")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    assert message.from_user, "Message has no user"
    await message.answer(f"Hola, {hbold(message.from_user.full_name)}!")


@router.message()
async def translate_video(message: types.Message) -> None:
    if not message.text:
        logger.warning(f"Invalid message received from telegram {message}")
        return

    if not message.from_user:
        logger.warning(f"No user found in message {message}")
        return

    result = Evaluator().evaluate(message.text, str(message.from_user.id))
    match result.action:
        case Action.TRANSLATE_VIDEO:
            from src.video.translator import Translator
            url_obj: HttpUrl = result.value
            await Translator().translate(url_obj, str(message.from_user.id))
        case Action.TRIGGER_TRANSLATION_LAMBDA:
            logger.info("Triggering translation lambda")