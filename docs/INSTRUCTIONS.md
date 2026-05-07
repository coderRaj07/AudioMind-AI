# 🚀 AudioMind-AI — Production-Grade Audio RAG System

AudioMind-AI is a scalable async Audio RAG (Retrieval-Augmented Generation) backend built with:

* FastAPI
* Async SQLAlchemy
* Temporal workflows
* Pinecone vector DB
* LangGraph orchestration
* Groq + Cerebras inference
* Deepgram transcription

The system allows users to:

1. Upload audio
2. Transcribe speech → text
3. Chunk + embed content
4. Store vectors in Pinecone
5. Query audio semantically using RAG

---

# 🧠 Architecture Overview

```text id="m5ycgb"
Audio Upload
    ↓
MinIO / S3 Storage
    ↓
Temporal Workflow
    ↓
Deepgram Transcription
    ↓
Chunking
    ↓
Embeddings
    ↓
Pinecone Vector DB
    ↓
LangGraph Retrieval
    ↓
Groq / Cerebras LLM
    ↓
Validated Response
```

---

# 🧱 Tech Stack

| Component         | Technology       |
| ----------------- | ---------------- |
| API Framework     | FastAPI          |
| DB                | PostgreSQL       |
| ORM               | Async SQLAlchemy |
| Vector DB         | Pinecone         |
| Workflow Engine   | Temporal         |
| Object Storage    | MinIO            |
| Transcription     | Deepgram         |
| LLM               | Groq             |
| LLM Fallback      | Cerebras         |
| RAG Orchestration | LangGraph        |
| Migrations        | Alembic          |
| Containerization  | Docker           |

---

# 📁 Project Structure

```text id="h3txlm"
AudioMind-AI/
│
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── ingestion/
│   ├── rag/
│   ├── schemas/
│   ├── services/
│   ├── workflows/
│   └── utils/
│
├── alembic/
│   ├── env.py
│   ├── versions/
│   └── script.py.mako
│
├── docker/
│   └── docker-compose.yml
│
├── scripts/
│   └── create_pinecone_index.py
│
├── tests/
│
├── .env
├── alembic.ini
├── requirements.txt
└── README.md
```

---

# 🚨 IMPORTANT CLEANUP

If you accidentally initialized Alembic inside docker:

```bash id="fgl2ol"
rm -rf docker/alembic
rm -f docker/alembic.ini
```

Alembic should ONLY exist at project root.

---

# ⚙️ Setup Instructions

---

# 1. Create Virtual Environment

```bash id="djlwmm"
python3 -m venv venv
```

Activate:

```bash id="vjlwmz"
source venv/bin/activate
```

---

# 2. Install Dependencies

```bash id="jlwmy8"
pip install --upgrade pip setuptools wheel

pip install -r requirements.txt
```

---

# 🔑 Generate API Keys

---

## ⚡ Groq API Key

### Console

[Groq Console](https://console.groq.com)

### API Keys

[Groq API Keys](https://console.groq.com/keys)

Example:

```env id="jlwm2z"
GROQ_API_KEY=gsk_xxxxx
```

---

## 🌲 Pinecone API Key

### Console

[Pinecone Console](https://app.pinecone.io)

### API Key Docs

[Pinecone API Key Docs](https://docs.pinecone.io/guides/projects/manage-api-keys)

Example:

```env id="jlwmql"
PINECONE_API_KEY=pcsk_xxxxx
```

---

## 🎤 Deepgram API Key

This project uses Deepgram for speech-to-text transcription because:

* better free tier
* low latency
* streaming support
* production-grade audio handling

### Console

[Deepgram Console](https://console.deepgram.com)

### Docs

[Deepgram Speech-to-Text Docs](https://developers.deepgram.com/docs/speech-to-text)

Example:

```env id="jlwmtk"
DEEPGRAM_API_KEY=xxxxx
```

---

## 🎧 OPTIONAL — Google Speech-to-Text

Recommended later for:

* enterprise streaming
* diarization
* realtime speech

### Console

[Google Cloud Console](https://console.cloud.google.com)

### Docs

[Google Speech-to-Text Docs](https://cloud.google.com/speech-to-text/docs)

---

# 🔐 Create `.env`

Create:

```bash id="jlwmmj"
nano .env
```

Paste:

```env id="jlwm97"
APP_NAME=voice-rag
ENV=development
DEBUG=true

DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/voice_rag

JWT_SECRET=supersecret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

PINECONE_API_KEY=YOUR_KEY
PINECONE_ENV=us-east-1
PINECONE_INDEX=voice-rag-index

S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minio
S3_SECRET_KEY=minio123
S3_BUCKET=audio-files

GROQ_API_KEY=YOUR_KEY
CEREBRAS_API_KEY=YOUR_KEY

DEEPGRAM_API_KEY=YOUR_KEY

TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default
TASK_QUEUE=audio-ingestion
```

---

# 🐳 Start Infrastructure

Go into docker folder:

```bash id="9xjlwm"
cd docker
```

Run:

```bash id="jlwm0u"
docker compose up -d
```

Verify:

```bash id="jlwmio"
docker ps
```

You should see:

* PostgreSQL
* Temporal
* MinIO

---

# 🪣 Create MinIO Bucket

Open:

```text id="jlwm4t"
http://localhost:9000
```

Login:

* username: `minio`
* password: `minio123`

Create bucket:

```text id="jlwm0h"
audio-files
```

---

# 🌲 Pinecone Setup (2 OPTIONS)

---

# ✅ OPTION 1 — Manual Pinecone Index Creation (Recommended)

Open:

[Pinecone Console](https://app.pinecone.io)

Click:

```text id="jlwm1x"
Create Index
```

Use EXACT settings:

| Setting    | Value           |
| ---------- | --------------- |
| Name       | voice-rag-index |
| Dimensions | 1536            |
| Metric     | cosine          |
| Type       | Dense           |
| Region     | us-east-1       |

---

## 🚨 IMPORTANT

DO NOT use:

```text id="b5jlwm"
512 dimensions
```

because your embedding model:

```text id="jlwmw4"
text-embedding-3-small
```

outputs:

```text id="jlwm77"
1536-dimensional vectors
```

---

# ✅ OPTION 2 — Automatic Pinecone Index Creation

Run from project root:

```bash id="c0jlwm"
python -m scripts.create_pinecone_index
```

⚠️ MUST use:

```bash id="n8jlwm"
python -m
```

NOT:

```bash id="jlwmvt"
python scripts/create_pinecone_index.py
```

Otherwise:

```text id="jlwm3f"
ModuleNotFoundError: app
```

---

# ⚙️ Alembic Setup

---

# Fix `alembic.ini`

ROOT FILE:

```text id="julwm4"
AudioMind-AI/alembic.ini
```

Use:

```ini id="jlwmjq"
[alembic]
script_location = alembic
prepend_sys_path = .

sqlalchemy.url = postgresql+asyncpg://user:password@localhost:5432/voice_rag


[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
```

---

# Fix `alembic/env.py`

Your Alembic config MUST use:

```python id="jlwmc8"
async_engine_from_config
```

NOT:

```python id="s9jlwm"
engine_from_config
```

Otherwise:

```text id="9njlwm"
MissingGreenlet
```

errors happen with async SQLAlchemy.

---

# 🗄️ Run Database Migrations

Back to project root:

```bash id="jlwm76"
cd ..
```

Generate migration:

```bash id="jlwmzt"
alembic revision --autogenerate -m "init"
```

Apply migration:

```bash id="jlwmgn"
alembic upgrade head
```

---

# ⚡ Start Temporal Worker

NEW TERMINAL:

```bash id="jlwm5a"
source venv/bin/activate
```

Run:

```bash id="jlwmzu"
python -m app.workflows.worker
```

---

# 🚀 Start FastAPI App

NEW TERMINAL:

```bash id="jlwmnz"
source venv/bin/activate
```

Run:

```bash id="j9jlwm"
uvicorn app.main:app --reload
```

Expected:

```text id="jlwm3m"
Running on http://127.0.0.1:8000
```

---

# 📘 Open Swagger Docs

Open:

```text id="jlwmxq"
http://localhost:8000/docs
```

Endpoints:

* `/upload`
* `/query`
* `/health`

---

# 🔐 Generate JWT Token

Run Python shell:

```python id="4tjlwm"
from app.core.security import create_access_token

token = create_access_token({"sub": "user-123"})
print(token)
```

---

# 🎤 Upload Audio

```http id="q3jlwm"
POST /upload
```

Header:

```text id="jlwm6w"
Authorization: Bearer YOUR_TOKEN
```

Upload `.wav`.

---

# 🔄 Verify Worker Processing

Worker logs should show:

* transcription
* chunking
* embeddings
* Pinecone upsert

---

# 🔎 Query Audio

```http id="jlwmjf"
POST /query
```

Body:

```json id="jlwm9r"
{
  "query": "What did I say about AI?"
}
```

---

# 🧪 Running Tests

```bash id="jlwmm2"
pytest
```

---

# 🚨 Common Errors

---

## ❌ MissingGreenlet

Cause:

* sync Alembic engine with async DB

Fix:

* use `async_engine_from_config`

---

## ❌ Pinecone Dimension Mismatch

Cause:

```text id="jlwm8j"
Index = 512
Embedding = 1536
```

Fix:

* recreate Pinecone index with `1536`

---

## ❌ ModuleNotFoundError: app

Cause:

```bash id="jlwm44"
python scripts/file.py
```

Fix:

```bash id="jalwm3"
python -m scripts.file
```

---

## ❌ Worker not processing

Cause:

* Temporal worker not running

Fix:

```bash id="jlwm3q"
python -m app.workflows.worker
```

---

# 🧠 Final Correct Startup Sequence

```text id="8qjlwm"
1. docker compose up -d
2. create Pinecone index (1536 dim)
3. alembic revision --autogenerate -m "init"
4. alembic upgrade head
5. python -m app.workflows.worker
6. uvicorn app.main:app --reload
```

---

# 🔥 Future Improvements

Potential next-level upgrades:

* streaming responses
* websocket transcription
* Redis caching
* multi-tenant namespaces
* observability (Prometheus + Grafana)
* Kubernetes deployment
* realtime voice assistant mode
