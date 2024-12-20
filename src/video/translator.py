from src.settings import get_settings
from src.video.downloader import Downloader
from src.core.s3_handler import S3Handler

class Translator:
    def __init__(self) -> None:
        self._settings = get_settings()
        self._s3_handler = S3Handler()

    async def translate_video(self, url: str) -> None:
        if self._settings.environment == 'dev':
            downloader = Downloader()
            video_path = await downloader.download_from_url(
                url,
                output_mode="path"
            )
            self._s3_handler.upload_file(video_path)
        else:
            # TODO: call another lambda to do the dowloading
            pass