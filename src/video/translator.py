from src.settings import get_settings
from src.video.compressor import Compressor
from src.video.downloader import Downloader
from src.video.uploader import Uploader
from src.core.helpers import validate_url

from loguru import logger

class Translator:
    # TODO: Use dependency injection
    def __init__(self) -> None:
        self._settings = get_settings()
        self._downloader = Downloader()
        self._uploader = Uploader()
        self._compressor = Compressor()

    def _get_video_from_bucket(self, video_id: str) -> None:
        # TODO: implement this
        return None

    async def translate_video(self, url: str, user_id: str) -> None:
        if not (url_obj := validate_url(url)):
            # TODO: send telegram message indicating that url isn't valid
            logger.warning(f"Invalid url received {url}")
            return

        if (self._get_video_from_bucket("fake_video_id")): # type: ignore
            return

        logger.info(f"Translating video at {url}")
        if self._settings.environment == 'dev':
            video_path = await self._downloader.download_from_url(
                url_obj,
                output_mode="path",
                user_id=user_id
            )
            compressed_path = self._compressor.compress_video(video_path, output_mode="path")
            self._uploader.upload_video(compressed_path, user_id)
        else:
            # TODO: call another lambda to do the dowloading
            pass