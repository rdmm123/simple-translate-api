from typing import Annotated
from fastapi import Depends
from aiogram import Bot, Dispatcher

from src.settings import Settings, get_settings
from src.telegram.bot import get_bot, get_dispatcher

SettingsDep = Annotated[Settings, Depends(get_settings)]
BotDep = Annotated[Bot, Depends(get_bot)]
DispatcherDep = Annotated[Dispatcher, Depends(get_dispatcher)]

if get_settings().runtime == 'server':
    from src.video.translator import Translator
    from src.video.compressor import Compressor
    from src.video.downloader import Downloader
    DownloaderDep = Annotated[Downloader, Depends(Downloader)]
    CompressorDep = Annotated[Compressor, Depends(Compressor)]
    TranslatorDep = Annotated[Translator, Depends(Translator)]
