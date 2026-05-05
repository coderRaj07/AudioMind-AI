from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from app.db.models import Audio, QueryLog


async def create_audio(
    db: AsyncSession,
    user_id: str,
    file_url: str,
):
    stmt = insert(Audio).values(
        user_id=user_id,
        file_url=file_url,
        status="processing",
    ).returning(Audio.id)

    result = await db.execute(stmt)
    await db.commit()

    return result.scalar_one()


async def log_query(
    db: AsyncSession,
    user_id: str,
    query: str,
    retrieved_chunks: str,
    response: str,
    confidence: float,
):
    stmt = insert(QueryLog).values(
        user_id=user_id,
        query=query,
        retrieved_chunks=retrieved_chunks,
        response=response,
        confidence=confidence,
    )
    await db.execute(stmt)
    await db.commit()