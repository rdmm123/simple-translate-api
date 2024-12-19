from typing import Annotated

from fastapi import (
    APIRouter,
    Body
)

from src.video.dowloader import download_video, download_video_stream
from src.video.compressor import Compressor

router = APIRouter(tags=["dev"], prefix="/dev")

@router.post("/quick_download")
def quick_download(
    video_id: Annotated[int, Body()], stream: Annotated[bool, Body()] = True
):
    compressor = Compressor()
    if stream:
        out = download_video_stream(video_id)
    else:
        out = download_video(video_id)

    path = compressor.compress_video(out, "path")

    return {"path": str(path)}
