from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.api.deps import get_current_user, get_db_session
from app.services.rag_service import run_rag
from app.db.crud import log_query

router = APIRouter()


@router.post("/query")
async def query_rag(
    body: dict,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    query = body.get("query")

    result = await run_rag(query, user["user_id"])

    answer = result.get("answer")
    chunks = result.get("chunks", [])

    # simple confidence
    confidence = 1.0 if chunks else 0.0

    await log_query(
        db,
        user["user_id"],
        query,
        json.dumps(chunks),
        answer,
        confidence,
    )

    return {
        "answer": answer,
        "citations": result.get("citations", [])
    }