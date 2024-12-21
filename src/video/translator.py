from src.settings import get_settings
from src.video.compressor import Compressor
from src.video.downloader import Downloader
from src.core.s3_handler import S3Handler
from src.core.helpers import validate_url

from loguru import logger

class Translator:
    # TODO: Use dependency injection
    def __init__(self) -> None:
        self._settings = get_settings()
        self._downloader = Downloader()
        self._s3_handler = S3Handler()
        self._compressor = Compressor()

    def _get_video_from_bucket(self, video_id: str) -> None:
        # TODO: implement this
        return None

    async def translate_video(self, url: str) -> None:
        if not validate_url(url):
            # TODO: send telegram message indicating that url isn't valid
            logger.warning(f"Invalid url received {url}")
            return

        if (self._get_video_from_bucket("fake_video_id")): # type: ignore
            return

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