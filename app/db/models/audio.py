import uuid
from sqlalchemy import Column, Text, Float, String, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base


class Audio(Base):
    __tablename__ = "audios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    file_url = Column(Text, nullable=False)
    duration = Column(Float, nullable=True)
    status = Column(String, nullable=False, default="processing")

    created_at = Column(TIMESTAMP, server_default=func.now())
