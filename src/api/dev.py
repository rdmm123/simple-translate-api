from typing import Annotated, IO
from pathlib import Path

from fastapi import (
    APIRouter,
    Body,
    HTTPException,
    status
)

from src.dependencies import CompressorDep, DownloaderDep

router = APIRouter(tags=["dev"], prefix="/dev")

@router.post("/quick_download")
def quick_download(
    downloader: DownloaderDep,
    compressor: CompressorDep,
    video_id: Annotated[int, Body()],
    stream: Annotated[bool, Body()] = True,

) -> dict[str, str]:
    out: IO[bytes] | Path | None = None
    if stream:
        out = downloader.download_video_stream(video_id)
    else:
        out = downloader.download_video(video_id)

    if not out:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="No output")

    path = compressor.compress_video(out, "path")

    return {"path": str(path)}
