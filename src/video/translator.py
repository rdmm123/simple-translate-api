from loguru import logger
from pydantic import HttpUrl

from src.settings import get_settings
from src.video.compressor import Compressor
from src.video.downloader import Downloader
from src.video.uploader import Uploader
from src.core.helpers import validate_url, url_to_filename


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

    async def _translate_path(self, url: HttpUrl, user_id: str) -> None:
        video_path = await self._downloader.download_from_url(
                url,
                output_mode="path",
                user_id=user_id
            )
        compressed_path = self._compressor.compress_video(video_path, output_mode="path")
        self._uploader.upload_video(compressed_path, user_id)

    async def _translate_stream(self, url: HttpUrl, user_id: str) -> None:
        download_stream = await self._downloader.download_from_url(
            url, output_mode="pipe", user_id=user_id
        )
        assert download_stream is not None, "No download stream found"
        compression_stream = self._compressor.compress_video(
            download_stream, output_mode="pipe"
        )
        self._uploader.upload_video_stream(
            compression_stream, f"{url_to_filename(url)}.mp4", user_id
        )

    async def translate_video(self, url: str, user_id: str) -> None:
        if not (url_obj := validate_url(url)):
            # TODO: send telegram message indicating that url isn't valid
            logger.warning(f"Invalid url received {url}")
            return

        if (self._get_video_from_bucket("fake_video_id")): # type: ignore
            return

        logger.info(f"Translating video at {url}")
        if self._settings.runtime == 'server':
            await self._translate_stream(url_obj, user_id)
        elif self._settings.runtime == 'lambda':
            # TODO: call another lambda to do the dowloading
            await self._translate_stream(url_obj, user_id)