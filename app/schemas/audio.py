from pydantic import BaseModel
from uuid import UUID


class UploadResponse(BaseModel):
    audio_id: UUID
    status: str