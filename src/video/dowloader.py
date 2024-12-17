
import re
import ffmpeg
from pathlib import Path

from playwright.async_api import Browser
from yt_dlp import YoutubeDL
from loguru import logger

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
        logger.info(f"{ydl}")
        info_dict = ydl.extract_info(url, download=False)
        video_title = info_dict.get('title', None)
        logger.info(f"Video found, downloading: {video_title}")

        logger.info(f"downloading {url}")
        #Download the video now
        ydl.download([url])

    return compress_video(download_path)

def compress_video(path: Path) -> Path:
    try:
        stream = ffmpeg.input(str(path))

        output_path = path.parent / f'compressed_{path.name}'
        output_path.unlink(missing_ok=True)

        logger.info(f"Compressing {path} into {output_path}")
        stream = ffmpeg.output(stream, str(output_path),
            vcodec='libx264',
            crf=23,
            preset='medium',
            acodec='aac',
            audio_bitrate='128k'
        )

        ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)

        return output_path
    except ffmpeg.Error as e:
        logger.error('An error occurred while compressing the video: ', e.stderr.decode())
        raise

async def download_from_url(browser: Browser, user: str, passw: str, url: str) -> Path:
    ctx = await browser.new_context()
    page = await ctx.new_page()

    logger.info("logging in")
    #the first URL (the login page)
    await page.goto(LOGIN_URL, wait_until='domcontentloaded')

    await page.wait_for_timeout(1_000)
    #Complete the login form
    await page.fill('input[name="log"]', user)
    await page.fill('input[name="pwd"]', passw)
    await page.click('input[type="submit"]')

    logger.info("log in succesful, going to video url")

    await page.goto(url, wait_until='domcontentloaded')

    #Search for the src selector that contains the vimeo.player of the video
    iframe = await page.query_selector("iframe[src*='vimeo.com']")

    if not iframe:
        raise VideoNotFound(f'Vimeo iframe not found in page {url}')

    video_Link = await iframe.get_attribute("src")
    await browser.close()
    logger.info("getting video id")
    id = get_id_video(video_Link)
    logger.info(f"video id = {id}")
    return download_video(id)
