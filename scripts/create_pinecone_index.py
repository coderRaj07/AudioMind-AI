from pinecone import Pinecone, ServerlessSpec
from app.core.config import get_settings

settings = get_settings()

pc = Pinecone(api_key=settings.PINECONE_API_KEY)

if settings.PINECONE_INDEX not in pc.list_indexes().names():
    pc.create_index(
        name=settings.PINECONE_INDEX,
        dimension=768,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region=settings.PINECONE_ENV
        )
    )