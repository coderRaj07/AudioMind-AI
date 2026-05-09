import re

from app.services.embedding_service import generate_embeddings
from app.services.pinecone_service import query_vectors
from app.core.logger import get_logger
from rank_bm25 import BM25Okapi

logger = get_logger(__name__)

SIMILARITY_THRESHOLD = 0.7


async def retrieve_chunks(query: str, user_id: str, audio_id: str | None = None):
    query = (query or "").strip()
    if not query:
        logger.warning("Empty query received in retrieve_chunks")
        return []

    # 1. Embed query with Jina AI
    query_embedding = (await generate_embeddings([query]))[0]

    # 2. Query Pinecone using the embedded query vector
    results = query_vectors(query_embedding, user_id, audio_id)
    matches = results.get("matches", []) if results else []

    if not matches:
        return []

    filtered = []
    for m in matches:
        score = m.get("score", 0)
        if score >= SIMILARITY_THRESHOLD:
            filtered.append(m)

    if not filtered:
        return []

    # Hybrid search: combine vector similarity with BM25 keyword matching
    texts = [m["metadata"]["text"] for m in filtered]
    tokenized_texts = [re.findall(r"\w+", text.lower()) for text in texts]
    bm25 = BM25Okapi(tokenized_texts)
    query_tokens = re.findall(r"\w+", query.lower())
    bm25_scores = bm25.get_scores(query_tokens)

    # Combine scores: vector score + normalized BM25 score
    for i, m in enumerate(filtered):
        vector_score = m["score"]
        bm25_score = bm25_scores[i]
        # Normalize BM25 to 0-1 roughly, assuming max BM25 is around len(query_tokens)
        normalized_bm25 = bm25_score / max(len(query_tokens), 1)
        combined_score = vector_score + 0.3 * normalized_bm25  # Weight BM25 at 30%
        m["score"] = combined_score

    # Sort by combined score
    filtered.sort(key=lambda x: x["score"], reverse=True)

    return filtered
