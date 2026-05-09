import re

# Lightweight reranker (score-based sort)

def _text_similarity(query: str, text: str) -> float:
    if not query or not text:
        return 0.0

    query_tokens = set(re.findall(r"\w+", query.lower()))
    text_tokens = set(re.findall(r"\w+", text.lower()))

    if not query_tokens or not text_tokens:
        return 0.0

    overlap = query_tokens.intersection(text_tokens)
    return len(overlap) / len(query_tokens)


# Lightweight reranker combining semantic score with text overlap.
def rerank_chunks(chunks, query: str | None = None):
    if query:
        return sorted(
            chunks,
            key=lambda x: (
                x.get("score", 0)
                + 0.15 * _text_similarity(query, x.get("metadata", {}).get("text", ""))
            ),
            reverse=True,
        )

    return sorted(chunks, key=lambda x: x.get("score", 0), reverse=True)