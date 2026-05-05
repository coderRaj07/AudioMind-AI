from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.api.deps import get_current_user, get_db_session
from app.services.rag_service import run_rag
from app.db.crud import log_query
from app.schemas.query import QueryRequest, QueryResponse

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_rag(
    body: QueryRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    result = await run_rag(body.query, user["user_id"])

    answer = result.get("answer")
    chunks = result.get("chunks", [])

    confidence = 1.0 if chunks else 0.0

    await log_query(
        db,
        user["user_id"],
        body.query,
        json.dumps(chunks),
        answer,
        confidence,
    )

    return QueryResponse(
        answer=answer,
        citations=result.get("citations", [])
    )