from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.api.deps import get_current_user, get_db_session
from app.db.repositories.query_repo import QueryRepository
from app.schemas.query import QueryRequest, QueryResponse

router = APIRouter()


def _serialize_chunk(chunk):
    if hasattr(chunk, "to_dict"):
        chunk = chunk.to_dict()

    if isinstance(chunk, dict):
        return {
            "id": chunk.get("id"),
            "score": chunk.get("score"),
            "metadata": chunk.get("metadata"),
        }

    if hasattr(chunk, "id") and hasattr(chunk, "score"):
        return {
            "id": getattr(chunk, "id", None),
            "score": getattr(chunk, "score", None),
            "metadata": getattr(chunk, "metadata", None),
        }

    return str(chunk)


@router.post("/query", response_model=QueryResponse)
async def query_rag(
    body: QueryRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    from app.services.rag_service import run_rag

    result = await run_rag(
        body.query,
        str(user.id),
        str(body.audio_id) if body.audio_id else None,
    )

    answer = result.get("answer")
    chunks = result.get("chunks", [])
    log_chunks = [_serialize_chunk(c) for c in chunks]

    confidence = 1.0 if chunks else 0.0

    query_repo = QueryRepository(db)
    await query_repo.log(
        user.id,
        body.query,
        json.dumps(log_chunks),
        answer,
        confidence,
    )

    return QueryResponse(
        answer=answer,
        citations=result.get("citations", [])
    )
