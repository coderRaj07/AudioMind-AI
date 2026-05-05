def test_chunking():
    from app.ingestion.chunking import chunk_text

    text = "hello world " * 100
    chunks = chunk_text(text)

    assert len(chunks) > 0