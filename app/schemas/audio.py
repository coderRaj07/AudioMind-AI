from pydantic import BaseModel
from uuid import UUID


class UploadResponse(BaseModel):
    audio_id: UUID
    status: str
    progress: float = 0.0


class AudioStatusResponse(BaseModel):
    audio_id: UUID
    status: str
    progress: float
