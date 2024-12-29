from typing import IO, Any
from pathlib import Path
from src.core.s3_handler import S3Handler

class Uploader:
    VIDEO_KEY = "{user_id}/original/{filename}"

    # TODO: Use dependency injection
    def __init__(self) -> None:
        self._s3_handler = S3Handler()

    def upload_video(self, file_path: Path, user_id: str) -> None:
        self._s3_handler.upload_file(
            file_path, self.VIDEO_KEY.format(user_id=user_id, filename=file_path.name)
        )

    def upload_video_stream(self, stream: IO[Any], filename: str, user_id: str) -> None:
        self._s3_handler.upload_file_obj(
            file_obj=stream,
            key=self.VIDEO_KEY.format(user_id=user_id, filename=filename)
        )