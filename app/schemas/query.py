from pydantic import BaseModel
from typing import List
from uuid import UUID


class QueryRequest(BaseModel):
    query: str
    audio_id: UUID | None = None


class QueryResponse(BaseModel):
    answer: str
    citations: List[str]