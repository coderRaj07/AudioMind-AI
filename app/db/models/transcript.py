import uuid
from sqlalchemy import Column, Text, Float, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base


class TranscriptChunk(Base):
    __tablename__ = "transcript_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    audio_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    text = Column(Text, nullable=False)
    start_time = Column(Float, nullable=True)
    end_time = Column(Float, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
