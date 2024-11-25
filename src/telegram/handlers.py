from aiogram import types
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.utils.markdown import hbold
from aiogram.types import Message

router = Router(name=__name__)

@router.message(Command("translate"))
async def cmd_id(message: Message) -> None:
    await message.answer("Envia la URL del video a traducir")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(f"Hola, {hbold(message.from_user.full_name)}!")


@router.message()
async def translate_video(message: types.Message) -> None:
    await message.answer("Descargando...")
