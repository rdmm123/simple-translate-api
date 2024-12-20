from src.settings import get_settings
from src.video.compressor import Compressor
from src.video.downloader import Downloader
from src.core.s3_handler import S3Handler

from loguru import logger

# TODO: Use dependency injection
class Translator:
    def __init__(self) -> None:
        self._settings = get_settings()
        self._downloader = Downloader()
        self._s3_handler = S3Handler()
        self._compressor = Compressor()

    async def translate_video(self, url: str) -> None:
        logger.info(f"Translating video at {url}")
        if self._settings.environment == 'dev':
            video_path = await self._downloader.download_from_url(
                url,
                output_mode="path"
            )
            compressed_path = self._compressor.compress_video(video_path, output_mode="path")
            self._s3_handler.upload_file(compressed_path)
        else:
            # TODO: call another lambda to do the dowloading
            pass