import uuid
from sqlalchemy import Column, String, Text, Float, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Audio(Base):
    __tablename__ = "audios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    file_url = Column(Text)
    duration = Column(Float)
    status = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())


class TranscriptChunk(Base):
    __tablename__ = "transcript_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True))
    audio_id = Column(UUID(as_uuid=True))

    text = Column(Text)
    start_time = Column(Float)
    end_time = Column(Float)

    created_at = Column(TIMESTAMP, server_default=func.now())


class QueryLog(Base):
    __tablename__ = "queries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True))

    query = Column(Text)
    retrieved_chunks = Column(Text)
    response = Column(Text)
    confidence = Column(Float)

    created_at = Column(TIMESTAMP, server_default=func.now())