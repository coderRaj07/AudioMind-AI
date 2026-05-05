from app.db.models.query import QueryLog
from app.db.repositories.base import BaseRepository


class QueryRepository(BaseRepository):

    async def log(
        self,
        user_id: str,
        query: str,
        retrieved_chunks: str,
        response: str,
        confidence: float,
    ):
        obj = QueryLog(
            user_id=user_id,
            query=query,
            retrieved_chunks=retrieved_chunks,
            response=response,
            confidence=confidence,
        )
        self.db.add(obj)
        await self.db.commit()
