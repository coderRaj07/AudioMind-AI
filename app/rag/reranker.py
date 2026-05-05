# Lightweight reranker (score-based sort)

def rerank_chunks(chunks):
    return sorted(chunks, key=lambda x: x.get("score", 0), reverse=True)