from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str
    ENV: str
    DEBUG: bool

    DATABASE_URL: str

    JWT_SECRET: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    PINECONE_API_KEY: str
    PINECONE_ENV: str
    PINECONE_INDEX: str

    S3_ENDPOINT: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET: str

    GROQ_API_KEY: str
    # GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # CEREBRAS_API_KEY: str
    # CEREBRAS_MODEL: str = "llama-4-scout-17b-16e-instruct"

    # EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    JINA_API_KEY: str
    JINA_EMBEDDING_MODEL: str = "jina-embeddings-v2-base-en"

    DEEPGRAM_API_KEY: str

    TEMPORAL_HOST: str
    TEMPORAL_NAMESPACE: str
    TASK_QUEUE: str

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()