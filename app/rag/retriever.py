import math
import re
from collections import Counter

from app.services.embedding_service import generate_embeddings
from app.services.pinecone_service import query_vectors
from app.core.logger import get_logger

logger = get_logger(__name__)

SIMILARITY_THRESHOLD = 0.7
BM25_K1 = 1.5
BM25_B = 0.75


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", (text or "").lower())


def _bm25_scores(document_tokens: list[list[str]], query_tokens: list[str]) -> list[float]:
    N = len(document_tokens)
    if N == 0 or not query_tokens:
        return [0.0] * len(document_tokens)

    avgdl = sum(len(doc) for doc in document_tokens) / N
    document_frequencies: dict[str, int] = {}
    term_frequencies: list[Counter[str]] = []

    for doc in document_tokens:
        counts = Counter(doc)
        term_frequencies.append(counts)
        for token in counts.keys():
            document_frequencies[token] = document_frequencies.get(token, 0) + 1

    scores: list[float] = []
    unique_query_terms = set(query_tokens)

    for i, doc in enumerate(document_tokens):
        score = 0.0
        doc_len = len(doc)
        for term in unique_query_terms:
            if term not in term_frequencies[i]:
                continue
            n_q = document_frequencies.get(term, 0)
            idf = math.log((N - n_q + 0.5) / (n_q + 0.5) + 1)
            f = term_frequencies[i][term]
            denom = f + BM25_K1 * (1 - BM25_B + BM25_B * (doc_len / avgdl))
            score += idf * ((f * (BM25_K1 + 1)) / denom)
        scores.append(score)

    return scores


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
    texts = [m.get("metadata", {}).get("text", "") for m in filtered]
    tokenized_texts = [_tokenize(text) for text in texts]
    query_tokens = _tokenize(query)
    bm25_scores = _bm25_scores(tokenized_texts, query_tokens)

    # Combine scores: vector score + normalized BM25 score
    for i, m in enumerate(filtered):
        vector_score = m["score"]
        bm25_score = bm25_scores[i]
        normalized_bm25 = bm25_score / max(len(query_tokens), 1)
        combined_score = vector_score + 0.3 * normalized_bm25
        m["score"] = combined_score

    # Sort by combined score
    filtered.sort(key=lambda x: x["score"], reverse=True)

    return filtered
