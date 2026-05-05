import uuid
from sqlalchemy import Column, Text, Float, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base


class QueryLog(Base):
    __tablename__ = "queries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    query = Column(Text, nullable=False)
    retrieved_chunks = Column(Text)
    response = Column(Text)
    confidence = Column(Float)

    created_at = Column(TIMESTAMP, server_default=func.now())
