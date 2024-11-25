from aiogram import types
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.utils.markdown import hbold
from aiogram.types import Message
from loguru import logger

from src.video.scraper import get_scraper
from src.video.dowloader import download_from_url
from src.settings import get_settings

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
    await message.answer("Descargando...")
    scraper = await get_scraper()
    logger.info(f"{scraper=}")
    settings = get_settings()

    browser = await scraper.get_browser()
    logger.info(f"{browser=}")
    await download_from_url(
        browser,
        settings.web_user,
        settings.web_pass,
        message.text
    )