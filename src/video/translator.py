from pydantic import HttpUrl

from src.video.compressor import Compressor
from src.video.downloader import Downloader
from src.video.uploader import Uploader
from src.settings import get_settings
from src.core.helpers import url_to_filename


class Translator:
    # TODO: Use dependency injection
    def __init__(self) -> None:
        self._settings = get_settings()
        self._downloader = Downloader()
        self._uploader = Uploader()
        self._compressor = Compressor()

    async def translate(self, url: HttpUrl, user_id: str) -> None:
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
