# AudioMind-AI

A production-grade **Audio RAG** backend — upload audio files, transcribe them via Deepgram, index the content into a vector database, and ask natural language questions about what was said.

---

## Features

- **Audio Ingestion Pipeline** — Upload `.wav` files, stored in MinIO (S3-compatible), transcribed via Deepgram (Nova-2), chunked, and embedded
- **Temporal Workflow Orchestration** — Reliable, retryable async processing with progress tracking
- **Hybrid Semantic Search** — Pinecone vector similarity + BM25 keyword scoring with reranking
- **RAG Pipeline (LangGraph)** — Retrieve → Rerank → Generate (Groq/Cerebras) → Validate (hallucination guard)
- **JWT Authentication** — Register/login flow with bcrypt password hashing
- **Async Everything** — FastAPI + async SQLAlchemy + async HTTP clients

## Tech Stack

| Component | Technology |
|-----------|------------|
| API | FastAPI + Uvicorn |
| Database | PostgreSQL 15 (asyncpg, SQLAlchemy 2.0) |
| Migrations | Alembic |
| Vector DB | Pinecone |
| Object Storage | MinIO (S3-compatible, boto3) |
| Workflow Engine | Temporal.io |
| Speech-to-Text | Deepgram (Nova-2) |
| LLM (Primary) | Groq (llama-3.3-70b) |
| LLM (Fallback) | Cerebras (llama-4-scout-17b) |
| Embeddings | Jina AI (jina-embeddings-v2-base-en) |
| RAG Orchestration | LangGraph |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Serialization | Pydantic v2 + Pydantic-Settings |
| Testing | pytest + pytest-asyncio |

## Architecture

```
Client ──► FastAPI ──┬──► /auth ──► JWT
                     ├──► /upload ──► MinIO ──► Temporal Worker ──┬──► Deepgram (STT)
                     │                                            ├──► Jina AI (Embed)
                     │                                            └──► Pinecone (Upsert)
                     └──► /query ──► LangGraph ──┬──► Pinecone (Retrieve)
                                                  ├──► Reranker
                                                  ├──► Groq/Cerebras (Generate)
                                                  └──► Validator
```

## Prerequisites

- Python 3.11+
- Docker & Docker Compose
- API keys for: Groq, Pinecone, Deepgram, Cerebras, Jina AI

## Quick Start

```bash
# 1. Clone and set up Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 3. Start infrastructure (PostgreSQL, MinIO, Temporal)
cd docker && docker compose up -d && cd ..

# 4. Create MinIO bucket
# Open http://localhost:9000 (minio / minio123), create bucket "audio-files"

# 5. Create Pinecone index
python -m scripts.create_pinecone_index

# 6. Run database migrations
alembic upgrade head

# 7. Start Temporal worker (separate terminal)
python -m app.workflows.worker

# 8. Start FastAPI
uvicorn app.main:app --reload
```

Or use the all-in-one script:

```bash
python -m scripts.start
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) for Swagger UI.

## Configuration

All config is via `.env` at the project root. Key variables:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string (`postgresql+asyncpg://...`) |
| `JWT_SECRET` | Secret key for JWT signing |
| `PINECONE_API_KEY` / `PINECONE_INDEX` | Pinecone vector DB credentials |
| `S3_ENDPOINT` / `S3_ACCESS_KEY` / `S3_SECRET_KEY` / `S3_BUCKET` | MinIO / S3 configuration |
| `GROQ_API_KEY` / `CEREBRAS_API_KEY` | LLM provider keys |
| `DEEPGRAM_API_KEY` | Speech-to-text API key |
| `JINA_API_KEY` | Embedding model API key |
| `TEMPORAL_HOST` / `TEMPORAL_NAMESPACE` / `TASK_QUEUE` | Temporal server config |

## API Endpoints

### Auth (`/auth`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/register` | No | Register with email + password |
| POST | `/auth/login` | No | Login, returns JWT |
| GET | `/auth/me` | JWT | Current user info |

### Upload (`/upload`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/upload` | JWT | Upload `.wav` file, triggers ingestion workflow |
| GET | `/audio/{audio_id}/status` | JWT | Check processing status & progress |

### Query (`/query`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/query` | JWT | Ask a natural language question about uploaded audio |

### Health

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | No | Health check |

## Ingestion Pipeline

```
Upload ──► MinIO ──► Temporal Workflow
                         │
                     ├── Download from MinIO
                     ├── Transcribe (Deepgram)
                     ├── Clean transcript
                     ├── Chunk text (300 words, 50 overlap)
                     ├── Embed (Jina AI)
                     ├── Upsert to Pinecone
                     └── Update status → completed
```

Progress is tracked in PostgreSQL at each stage (10%, 25%, 45%, 65%, 85%, 100%).

## RAG Pipeline

```
Query ──► 1. Retrieve (Pinecone vector + BM25 hybrid search)
       ──► 2. Rerank (semantic score + text overlap, top-3)
       ──► 3. Generate (Groq → Cerebras fallback)
       ──► 4. Validate (≥30% word overlap with context to prevent hallucination)
       ──► Answer + Citations
```

## Project Structure

```
AudioMind-AI/
├── app/
│   ├── main.py                     # FastAPI app entry point
│   ├── api/                        # Route handlers (auth, upload, query, health)
│   ├── core/                       # Config, security, exceptions, logging
│   ├── db/                         # Models, session, repositories
│   ├── ingestion/                  # Chunking, text cleaning
│   ├── rag/                        # LangGraph pipeline (retriever, reranker, generator, validator)
│   ├── services/                   # External service integrations (Deepgram, Pinecone, Jina, LLM, S3)
│   ├── schemas/                    # Pydantic request/response models
│   ├── workflows/                  # Temporal workflow definitions & worker
│   ├── utils/                      # Retry, IDs, time helpers
│   └── tests/                      # pytest test suite
├── alembic/                        # Database migrations
├── docker/                         # Docker Compose (PostgreSQL, MinIO, Temporal)
├── scripts/                        # Utility scripts (start, seed, create index)
├── .env.example
└── requirements.txt
```

## Testing

```bash
pytest
```

## Infrastructure

The `docker/docker-compose.yml` launches:
- **PostgreSQL 15** — primary database (port 5432)
- **MinIO** — S3-compatible object storage (ports 9000, 9001)
- **Temporal Server** — workflow engine (port 7233)
- **Temporal UI** — workflow visibility (port 8233)

## License

This project is private / proprietary.
