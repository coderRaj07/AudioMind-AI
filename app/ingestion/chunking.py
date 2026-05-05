from typing import List, Dict


def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> List[Dict]:
    words = text.split()
    chunks = []

    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]

        chunk_text = " ".join(chunk_words)

        chunks.append({
            "text": chunk_text,
            "start_time": 0.0,
            "end_time": 0.0
        })

        start += chunk_size - overlap

    return chunks