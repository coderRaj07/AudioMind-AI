from app.services.embedding_service import generate_embeddings
from app.services.pinecone_service import query_vectors
from app.core.logger import get_logger

logger = get_logger(__name__)

SIMILARITY_THRESHOLD = 0.7


async def retrieve_chunks(query: str, user_id: str):
    # 1. Embed query
    query_embedding = (await generate_embeddings([query]))[0]

    # 2. Query Pinecone
    results = query_vectors(query_embedding, user_id)

    matches = results.get("matches", [])

    if not matches:
        return []

    filtered = []
    for m in matches:
        score = m.get("score", 0)
        if score >= SIMILARITY_THRESHOLD:
            filtered.append(m)

    return filtered