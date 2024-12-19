import io
import re

import subprocess

from pathlib import Path
from yt_dlp import YoutubeDL
from loguru import logger

from src.scraper import Scraper
from src.settings import get_settings

# TODO: Download, compress and upload chunk by chunk

LOGIN_URL = 'https://autismpartnershipfoundation.org/log-in/'
VIMEO_ID_URL = 'https://vimeo.com/{id}'


class VideoNotFound(Exception):
    pass


def get_id_video(url: str):
    # Regular expression to find the ID after "/video/"
    match = re.search(r'\/video\/(\d+)', url)
    if match:
        return match.group(1)  # Returns the first group (the ID)
    else:
        return None  # If the ID is not found


def download_video(id: int) -> Path:
    #Path where the downloaded video will be saved
    download_dir = Path('/tmp') # TODO: Replace with TemporaryDirectory
    download_dir.mkdir(exist_ok=True)

    url = VIMEO_ID_URL.format(id=id)
    logger.info(f"Downloading video at {url}")

    download_path = download_dir / 'video.mp4'
    download_path.unlink(missing_ok=True)
    #Setting yt-dlp to get video title
    ydl_opts = {
        'format': 'bv+ba',
        'outtmpl': str(download_path),
        'quiet': True,
        'no_warnings': True
    }

    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        video_title = info_dict.get('title', None)
        logger.info(f"Video found, downloading: {video_title}")

        logger.info(f"downloading {url}")
        #Download the video now
        ydl.download([url])

    return download_path


def download_video_stream(id: int) -> io.BufferedReader:
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
        # stderr=subprocess.DEVNULL # don't fill up server logs
    )

    return downloader_proc.stdout


async def get_video_id_from_url(url: str) -> str:
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
    iframe = await page.query_selector("iframe[src*='vimeo.com']")

    if not iframe:
        raise VideoNotFound(f'Vimeo iframe not found in page {url}')

    video_link = await iframe.get_attribute("src")

    await browser.close()
    return get_id_video(video_link)


async def download_from_url(url: str) -> Path:
    video_id = get_video_id_from_url(url)
    return download_video(video_id)


async def download_from_url_stream(url: str) -> io.BufferedReader:
    video_id = get_video_id_from_url(url)
    return download_video_stream(video_id)