from typing import Annotated
from fastapi import Depends

from src.video.compressor import Compressor
from src.video.dowloader import Downloader
from src.settings import Settings, get_settings

SettingsDep = Annotated[Settings, Depends(get_settings)]
DownloaderDep = Annotated[Downloader, Depends(Downloader)]
CompressorDep = Annotated[Compressor, Depends(Compressor)]