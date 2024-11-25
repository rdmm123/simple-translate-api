
import os
import re
import subprocess

from playwright.async_api import Browser
from yt_dlp import YoutubeDL
from loguru import logger

LOGIN_URL = 'https://autismpartnershipfoundation.org/all-courses/my-account/'
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


def download_video(id: int):
    logger.info("downloading video")
    #Path where the downloaded video will be saved
    download_path = 'VideosVimeo/'
    os.makedirs(download_path, exist_ok=True)

    url = VIMEO_ID_URL.format(id=id)

    logger.info("URl original video vimeo: ",url)
    #Setting yt-dlp to get video title
    ydl_opts = {
        'format': 'bv+ba',
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'), #Use the original title of the video
        'quiet': True,  #Suppress output of download process
    }

    #Download the video using yt-dlp
    with YoutubeDL(ydl_opts) as ydl:
        logger.info(f"{ydl}")
        info_dict = ydl.extract_info(url, download=False)  # We only extract the information without downloading it yet
        video_title = info_dict.get('title', None)  #get the video title
        print(f"Video descargado con el título: {video_title}")

        logger.info(f"downloading {url}")
        #Download the video now
        ydl.download([url])

    # path of the downloaded video
    input_filename = os.path.join(download_path, f'{video_title}.mp4')

    # path of the compressed file
    compressed_filename = os.path.join(download_path, f'{video_title}_comprimido.mp4')

    logger.info('downlaod complete. compressing video')
    # ffmpeg settings to download the compressed video
    ffmpeg_command = [
        'ffmpeg',
        '-i', input_filename,                 # input file
        '-c:v', 'libx264',                    # H.264 video codec
        '-crf', '23',                         # Video quality (adjustable)
        '-preset', 'medium',                  # Compression speed preset
        '-c:a', 'aac',                        # AAC audio codec
        '-b:a', '128k',                       # Audio bit rate
        compressed_filename                   # compressed output file
    ]

    #Run FFmpeg to compress the video
    subprocess.run(ffmpeg_command)
    logger.info(f"Video comprimido guardado como: {compressed_filename}")

async def download_from_url(browser: Browser, user: str, passw: str, url: str):
    ctx = await browser.new_context()
    page = await ctx.new_page()

    logger.info("logging in")
    #the first URL (the login page)
    await page.goto(LOGIN_URL)

    #Complete the login form

    await page.fill('input[name="username"]', user)
    await page.fill('input[name="password"]', passw)
    await page.click('button[type="submit"]')

    logger.info("log in succesful, going to video url")

    await page.goto(url)

    #Search for the src selector that contains the vimeo.player of the video
    iframe = await page.query_selector("iframe[src*='vimeo.com']")

    if not iframe:
        raise VideoNotFound(f'Vimeo iframe not found in page {url}')

    video_Link = await iframe.get_attribute("src")
    browser.close()
    logger.info("getting video id")
    id = get_id_video(video_Link)
    logger.info(f"video id = {id}")
    download_video(id)
