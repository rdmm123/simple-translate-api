from typing import Annotated, IO, cast
from pathlib import Path

from pydantic import BaseModel
from fastapi import (
    APIRouter,
    Body,
    HTTPException,
    status
)

from src.dependencies import CompressorDep, DownloaderDep
from src.core.s3_handler import S3Handler


router = APIRouter(tags=["dev"], prefix="/dev")


@router.post("/quick_download")
def quick_download(
    downloader: DownloaderDep,
    compressor: CompressorDep,
    video_id: Annotated[int, Body()],
    stream: Annotated[bool, Body()] = True,
    compress: Annotated[bool, Body()] = True
) -> dict[str, str]:
    out: IO[bytes] | Path | None = None
    if stream and compress:
        out = downloader.download_video_stream(video_id)
    else:
        out = downloader.download_video(video_id)

    if not out:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="No output")

    if compress:
        path = compressor.compress_video(out, "path")
    else:
        path = cast(Path, out)

    return {"path": str(path)}


class QuickCompressBody(BaseModel):
    input_path: Path

@router.post("/quick_compress")
def quick_compress(
    compressor: CompressorDep,
    body: Annotated[QuickCompressBody, Body()]
) -> dict[str, str]:
    path = compressor.compress_video(body.input_path, 'path')
    return {"path": str(path)}


class QuickUploadBody(BaseModel):
    file_path: Path
    key: str | None = None

@router.post("/quick_upload")
def quick_upload(
    body: Annotated[QuickUploadBody, Body()]
) -> dict[str, str]:
    s3_handler = S3Handler()
    key = s3_handler.upload_file(body.file_path)
    return {"key": key}
