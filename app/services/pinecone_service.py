from pinecone import Pinecone
from app.core.config import get_settings
from app.core.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)

pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX)


def upsert_vectors(vectors):
    try:
        index.upsert(vectors=vectors)
    except Exception as e:
        logger.error(f"Pinecone upsert failed: {e}")
        raise


def query_vectors(vector, user_id, top_k=5):
    try:
        return index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=True,
            filter={"user_id": {"$eq": user_id}},
        )
    except Exception as e:
        logger.error(f"Pinecone query failed: {e}")
        raise