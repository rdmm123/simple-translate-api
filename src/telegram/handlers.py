from aiogram import types
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.utils.markdown import hbold
from aiogram.types import Message

from src.scraper import Scraper
from src.video.dowloader import download_from_url
from src.settings import get_settings
from src.s3_client import S3Client

router = Router(name=__name__)


@router.message(Command("translate"))
async def cmd_id(message: Message) -> None:
    await message.answer("Envia la URL del video a traducir")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(f"Hola, {hbold(message.from_user.full_name)}!")


@router.message()
async def translate_video(message: types.Message) -> None:
    # TODO: Validate url first
    # TODO: check if video already in bucket first
    settings = get_settings()
    s3_client = S3Client()

    if settings.environment == 'dev':
        scraper = await Scraper.create()
        browser = await scraper.get_browser()
        video_path = await download_from_url(
            browser,
            settings.web_user,
            settings.web_pass,
            message.text
        )
        s3_client.upload_file(video_path)
    else:
        # TODO: call another lambda to do the dowloading
        pass