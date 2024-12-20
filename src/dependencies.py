from typing import Annotated
from fastapi import Depends

from src.video.compressor import Compressor
from src.video.downloader import Downloader
from src.video.translator import Translator
from src.settings import Settings, get_settings

SettingsDep = Annotated[Settings, Depends(get_settings)]
DownloaderDep = Annotated[Downloader, Depends(Downloader)]
CompressorDep = Annotated[Compressor, Depends(Compressor)]
TranslatorDep = Annotated[Translator, Depends(Translator)]