from pydantic import BaseModel, HttpUrl

class TranslateVideoCommand(BaseModel):
    video_url: HttpUrl
    user_id: str