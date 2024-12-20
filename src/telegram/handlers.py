from aiogram import types
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.utils.markdown import hbold
from aiogram.types import Message

from src.video.dowloader import Downloader
from src.settings import get_settings
from src.core.s3_handler import S3Handler

from loguru import logger

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
    # TODO: Validate url first
    # TODO: check if video already in bucket first
    settings = get_settings()
    s3_handler = S3Handler()

    if not message.text:
        logger.warning(f"Invalid message received from telegram {message}")
        return

    if settings.environment == 'dev':
        downloader = Downloader()
        video_path = await downloader.download_from_url(
            message.text,
            output_mode="path"
        )
        s3_handler.upload_file(video_path)
    else:
        # TODO: call another lambda to do the dowloading
        pass