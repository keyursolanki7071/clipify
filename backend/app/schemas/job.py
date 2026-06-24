import uuid
from pydantic import BaseModel, HttpUrl

class JobCreate(BaseModel):
    youtube_url: str # Using str instead of HttpUrl to keep it simple, we can validate the format later.

class JobResponse(BaseModel):
    id: uuid.UUID
    youtube_url: str
    status: str
    progress: float
    video_title: str | None = None
    video_thumbnail: str | None = None
    video_duration: int | None = None
    result_paths: dict | None = None
    error_message: str | None = None

    model_config = {
        "from_attributes": True
    }
