from pathlib import Path
from src.core.s3_handler import S3Handler

class Uploader:
    VIDEO_KEY = "{user_id}/original/{filename}"

    # TODO: Use dependency injection
    def __init__(self):
        self._s3_handler = S3Handler()

    def upload_video(self, file_path: Path, user_id: str):
        self._s3_handler.upload_file(
            file_path, self.VIDEO_KEY.format(user_id=user_id, filename=file_path.name)
        )

    def upload_video_stream(self):
        pass