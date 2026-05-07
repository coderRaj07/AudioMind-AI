# 🚀 How To Run Your Voice RAG System (End-to-End)

This is the complete production-style startup flow for your:

* FastAPI backend
* PostgreSQL
* Temporal
* Pinecone
* MinIO/S3
* LangGraph RAG pipeline

---

# 🧱 1. Final Project Structure

Your root should look like:

```text id="mjlwm4"
voice_rag_system/
│
├── app/
├── alembic/
├── docker/
├── scripts/
│
├── .env
├── alembic.ini
├── requirements.txt
```

---

# ⚙️ 2. Create Python Environment

## Create venv

```bash id="5t26wb"
python3 -m venv venv
```

---

## Activate

### Linux/macOS

```bash id="i3a8h3"
source venv/bin/activate
```

---

# 📦 3. Install Dependencies

```bash id="g7wtwm"
pip install --upgrade pip setuptools wheel

pip install -r requirements.txt
```

---

# 🔐 4. Create `.env`

At project root:

```bash id="qfxykg"
nano .env
```

Paste:

```env id="w9sk3t"
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

WHISPER_API_KEY=YOUR_KEY

TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default
TASK_QUEUE=audio-ingestion
```

---

# 🐳 5. Start Infrastructure

Go to docker folder:

```bash id="jjigso"
cd docker
```

Run:

```bash id="06ce8y"
docker compose up -d
```

This starts:

* PostgreSQL
* Temporal
* MinIO

---

# ✅ Verify containers

```bash id="k0v95u"
docker ps
```

---

# 🪣 6. Create MinIO Bucket

Open:

```text id="ohwxjlwm"
http://localhost:9000
```

Login:

* user: `minio`
* password: `minio123`

Create bucket:

```text id="lfasf6"
audio-files
```

---

# 🗄️ 7. Run Alembic Migration

Back to project root:

```bash id="l0doh7"
cd ..
```

Generate migration:

```bash id="1q5lu5"
alembic revision --autogenerate -m "init"
```

Apply migration:

```bash id="87i57l"
alembic upgrade head
```

---

# 🔍 8. Create Pinecone Index

Run:

```bash id="wl9lq7"
python scripts/create_pinecone_index.py
```

Expected:

```text id="i33s0r"
Index ready
```

---

# ⚡ 9. Start Temporal Worker

VERY IMPORTANT.

New terminal:

```bash id="cjlwmx"
source venv/bin/activate
```

Run worker:

```bash id="3o3ivg"
python -m app.workflows.worker
```

Expected:

```text id="z7xhyl"
Worker started
```

---

# 🚀 10. Start FastAPI App

New terminal:

```bash id="y8e3px"
source venv/bin/activate
```

Run:

```bash id="6q1slh"
uvicorn app.main:app --reload
```

Expected:

```text id="fy1tvx"
Uvicorn running on http://127.0.0.1:8000
```

---

# 📘 11. Open Swagger Docs

Open:

```text id="78jlsb"
http://localhost:8000/docs
```

You’ll see:

* `/upload`
* `/query`
* `/health`

---

# 🔐 12. Generate JWT Token (temporary testing)

Python shell:

```python id="jlwmj6"
from app.core.security import create_access_token

token = create_access_token({"sub": "user-123"})
print(token)
```

---

# 🎤 13. Test Upload API

In Swagger:

```http id="b53r5m"
POST /upload
```

Headers:

```text id="0ux0fc"
Authorization: Bearer YOUR_TOKEN
```

Upload `.wav` file.

Expected:

```json id="ffh5ye"
{
  "audio_id": "...",
  "status": "processing"
}
```

---

# 🔄 14. Verify Temporal Processing

Worker terminal should show:

* workflow execution
* transcription
* embeddings
* Pinecone upsert

---

# 🔎 15. Query Your Audio

```http id="2a6czm"
POST /query
```

Body:

```json id="3w5n0j"
{
  "query": "What did I say about AI?"
}
```

Headers:

```text id="4d88hx"
Authorization: Bearer YOUR_TOKEN
```

Expected:

```json id="gkn4ee"
{
  "answer": "...",
  "citations": [
    "[Chunk 1 | 0–0]"
  ]
}
```

---

# 🧠 Complete Runtime Architecture

```text id="h2d0mp"
Upload API
   ↓
S3 (MinIO)
   ↓
Temporal Workflow
   ↓
Whisper
   ↓
Chunking
   ↓
Embeddings
   ↓
Pinecone

Query API
   ↓
LangGraph
   ↓
Retriever
   ↓
LLM
   ↓
Validator
   ↓
Response
```

---

# 🚨 Common Errors (VERY IMPORTANT)

## ❌ Pinecone dimension mismatch

Your embedding dimension MUST match index dimension.

Example:

* `1536`
* `1024`

---

## ❌ Worker not running

Upload succeeds but processing never happens.

Fix:

```bash id="ggu0f8"
python -m app.workflows.worker
```

---

## ❌ Missing bucket

MinIO error:

```text id="jlwm36"
NoSuchBucket
```

Create:

```text id="jlwmxq"
audio-files
```

---

## ❌ Async DB errors

Usually:

* wrong DB URL
* missing `asyncpg`

---

# 🔥 Production Deployment Later

You can later deploy:

* FastAPI → Railway / EC2 / Kubernetes
* Worker → separate worker nodes
* Postgres → NeonDB
* MinIO → S3
* Temporal → Temporal Cloud
* Pinecone → managed

---

# 🧠 Final Startup Sequence (memorize this)

```text id="jlwm0z"
1. docker compose up
2. alembic upgrade head
3. create Pinecone index
4. start Temporal worker
5. start FastAPI
```
# 🚀 How To Run Your Voice RAG System (End-to-End)

This is the complete production-style startup flow for your:

* FastAPI backend
* PostgreSQL
* Temporal
* Pinecone
* MinIO/S3
* LangGraph RAG pipeline

---

# 🧱 1. Final Project Structure

Your root should look like:

```text id="mjlwm4"
voice_rag_system/
│
├── app/
├── alembic/
├── docker/
├── scripts/
│
├── .env
├── alembic.ini
├── requirements.txt
```

---

# ⚙️ 2. Create Python Environment

## Create venv

```bash id="5t26wb"
python3 -m venv venv
```

---

## Activate

### Linux/macOS

```bash id="i3a8h3"
source venv/bin/activate
```

---

# 📦 3. Install Dependencies

```bash id="g7wtwm"
pip install -r requirements.txt
```

---

# 🔐 4. Create `.env`

At project root:

```bash id="qfxykg"
nano .env
```

Paste:

```env id="w9sk3t"
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

WHISPER_API_KEY=YOUR_KEY

TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default
TASK_QUEUE=audio-ingestion
```

---

# 🐳 5. Start Infrastructure

Go to docker folder:

```bash id="jjigso"
cd docker
```

Run:

```bash id="06ce8y"
docker compose up -d
```

This starts:

* PostgreSQL
* Temporal
* MinIO

---

# ✅ Verify containers

```bash id="k0v95u"
docker ps
```

---

# 🪣 6. Create MinIO Bucket

Open:

```text id="ohwxjlwm"
http://localhost:9000
```

Login:

* user: `minio`
* password: `minio123`

Create bucket:

```text id="lfasf6"
audio-files
```

---

# 🗄️ 7. Run Alembic Migration

Back to project root:

```bash id="l0doh7"
cd ..
```

Generate migration:

```bash id="1q5lu5"
alembic revision --autogenerate -m "init"
```

Apply migration:

```bash id="87i57l"
alembic upgrade head
```

---

# 🔍 8. Create Pinecone Index

Run:

```bash id="wl9lq7"
python scripts/create_pinecone_index.py
```

Expected:

```text id="i33s0r"
Index ready
```

---

# ⚡ 9. Start Temporal Worker

VERY IMPORTANT.

New terminal:

```bash id="cjlwmx"
source venv/bin/activate
```

Run worker:

```bash id="3o3ivg"
python -m app.workflows.worker
```

Expected:

```text id="z7xhyl"
Worker started
```

---

# 🚀 10. Start FastAPI App

New terminal:

```bash id="y8e3px"
source venv/bin/activate
```

Run:

```bash id="6q1slh"
uvicorn app.main:app --reload
```

Expected:

```text id="fy1tvx"
Uvicorn running on http://127.0.0.1:8000
```

---

# 📘 11. Open Swagger Docs

Open:

```text id="78jlsb"
http://localhost:8000/docs
```

You’ll see:

* `/upload`
* `/query`
* `/health`

---

# 🔐 12. Generate JWT Token (temporary testing)

Python shell:

```python id="jlwmj6"
from app.core.security import create_access_token

token = create_access_token({"sub": "user-123"})
print(token)
```

---

# 🎤 13. Test Upload API

In Swagger:

```http id="b53r5m"
POST /upload
```

Headers:

```text id="0ux0fc"
Authorization: Bearer YOUR_TOKEN
```

Upload `.wav` file.

Expected:

```json id="ffh5ye"
{
  "audio_id": "...",
  "status": "processing"
}
```

---

# 🔄 14. Verify Temporal Processing

Worker terminal should show:

* workflow execution
* transcription
* embeddings
* Pinecone upsert

---

# 🔎 15. Query Your Audio

```http id="2a6czm"
POST /query
```

Body:

```json id="3w5n0j"
{
  "query": "What did I say about AI?"
}
```

Headers:

```text id="4d88hx"
Authorization: Bearer YOUR_TOKEN
```

Expected:

```json id="gkn4ee"
{
  "answer": "...",
  "citations": [
    "[Chunk 1 | 0–0]"
  ]
}
```

---

# 🧠 Complete Runtime Architecture

```text id="h2d0mp"
Upload API
   ↓
S3 (MinIO)
   ↓
Temporal Workflow
   ↓
Whisper
   ↓
Chunking
   ↓
Embeddings
   ↓
Pinecone

Query API
   ↓
LangGraph
   ↓
Retriever
   ↓
LLM
   ↓
Validator
   ↓
Response
```

---

# 🚨 Common Errors (VERY IMPORTANT)

## ❌ Pinecone dimension mismatch

Your embedding dimension MUST match index dimension.

Example:

* `1536`
* `1024`

---

## ❌ Worker not running

Upload succeeds but processing never happens.

Fix:

```bash id="ggu0f8"
python -m app.workflows.worker
```

---

## ❌ Missing bucket

MinIO error:

```text id="jlwm36"
NoSuchBucket
```

Create:

```text id="jlwmxq"
audio-files
```

---

## ❌ Async DB errors

Usually:

* wrong DB URL
* missing `asyncpg`

---

# 🔥 Production Deployment Later

You can later deploy:

* FastAPI → Railway / EC2 / Kubernetes
* Worker → separate worker nodes
* Postgres → NeonDB
* MinIO → S3
* Temporal → Temporal Cloud
* Pinecone → managed

---

# 🧠 Final Startup Sequence (memorize this)

```text id="jlwm0z"
1. docker compose up
2. alembic upgrade head
3. create Pinecone index
4. start Temporal worker
5. start FastAPI
```
