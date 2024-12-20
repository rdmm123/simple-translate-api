import re
import subprocess
from typing import Literal, overload, IO

from pathlib import Path
from yt_dlp import YoutubeDL, YDLOpts
from loguru import logger

from src.core.scraper import Scraper
from src.settings import get_settings

# TODO: Download, compress and upload chunk by chunk

LOGIN_URL = 'https://autismpartnershipfoundation.org/log-in/'
VIMEO_ID_URL = 'https://vimeo.com/{id}'


class VideoNotFound(Exception):
    pass

class Downloader:
    def _get_video_id(self, url: str) -> int | None:
        # Regular expression to find the ID after "/video/"
        match = re.search(r'\/video\/(\d+)', url)
        if match:
            return int(match.group(1))  # Returns the first group (the ID)
        else:
            return None  # If the ID is not found


    def download_video(self, id: int) -> Path:
        #Path where the downloaded video will be saved
        download_dir = Path('/tmp') # TODO: Replace with TemporaryDirectory
        download_dir.mkdir(exist_ok=True)

        url = VIMEO_ID_URL.format(id=id)
        logger.info(f"Downloading video at {url}")

        download_path = download_dir / 'video.mp4'
        download_path.unlink(missing_ok=True)
        #Setting yt-dlp to get video title
        ydl_opts: YDLOpts = {
            'format': 'bv+ba',
            'outtmpl': str(download_path),
            'quiet': True,
            'no_warnings': True,
            'logger': logger
        }

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False) # type: ignore
            video_title = info_dict.get('title', None)
            logger.info(f"Video found, downloading: {video_title}")

            logger.info(f"downloading {url}")
            #Download the video now
            ydl.download([url])

        return download_path


    def download_video_stream(self, id: int) -> IO[bytes] | None:
        #Path where the downloaded video will be saved
        url = VIMEO_ID_URL.format(id=id)
        logger.info(f"Downloading video at {url}")

        args = [
            # request to download with video ID
            "yt-dlp", url,
            # output to stdout (needed for streaming)
            "-o", "-",
            # specify output format
            "-f", "bv+ba",
        ]

        downloader_proc = subprocess.Popen(
            args,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL # don't fill up server logs
        )

        return downloader_proc.stdout


    async def _get_video_id_from_url(self, url: str) -> int:
        scraper = await Scraper.create()
        browser = await scraper.get_browser()
        settings = get_settings()

        page = await browser.new_page()

        logger.info("logging in")
        #the first URL (the login page)
        await page.goto(LOGIN_URL, wait_until='domcontentloaded')
        await page.wait_for_timeout(1_000)
        #Complete the login form
        await page.fill('input[name="log"]', settings.web_user)
        await page.fill('input[name="pwd"]', settings.web_pass)
        await page.click('input[type="submit"]')

        logger.info("log in succesful, going to video url")
        await page.goto(url, wait_until='domcontentloaded')

        #Search for the src selector that contains the vimeo.player of the video
        if not (iframe := await page.query_selector("iframe[src*='vimeo.com']")):
            raise VideoNotFound(f'Vimeo iframe not found in page {url}')

        if not (video_link := await iframe.get_attribute("src")):
            raise VideoNotFound(f"Video url not found in page {url}")

        await browser.close()

        if not (video_id := self._get_video_id(video_link)):
            raise VideoNotFound(f"Video id not found in {video_link}")

        return video_id


    async def _download_from_url(self, url: str) -> Path:
        video_id = await self._get_video_id_from_url(url)
        return self.download_video(video_id)


    async def _download_from_url_stream(self, url: str) -> IO[bytes] | None:
        video_id = await self._get_video_id_from_url(url)
        return self.download_video_stream(video_id)

    @overload
    async def download_from_url(self, url: str, output_mode: Literal["path"]) -> Path: ...
    @overload
    async def download_from_url(self, url: str, output_mode: Literal["pipe"]) -> IO[bytes] | None: ...
    async def download_from_url(self, url: str, output_mode: Literal["path", "pipe"]) -> Path | IO[bytes] | None:
        if output_mode == "path":
            return await self._download_from_url(url)
        else:
            return await self._download_from_url_stream(url)
