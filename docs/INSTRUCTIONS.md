# 🚀 FINAL COMPLETE SETUP GUIDE — AudioMind-AI

This setup contains:

* ✅ Async Alembic fixes
* ✅ Pinecone setup
* ✅ API key generation links
* ✅ Proper module execution
* ✅ Correct startup order
* ✅ Two Pinecone creation options (manual + automated)

Based on latest debugging/setup state. 

---

# 🧱 1. Correct Project Structure

```text id="8jjlwm"
AudioMind-AI/
│
├── app/
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
├── .env
├── alembic.ini
├── requirements.txt
```

---

# 🚨 IMPORTANT CLEANUP

Delete accidental Docker Alembic setup:

```bash id="4xjlwm"
rm -rf docker/alembic
rm -f docker/alembic.ini
```

---

# ⚙️ 2. Create Virtual Environment

```bash id="jlwm4z"
python3 -m venv venv
```

Activate:

```bash id="jlwm18"
source venv/bin/activate
```

---

# 📦 3. Install Dependencies

```bash id="jlwmmz"
pip install --upgrade pip setuptools wheel

pip install -r requirements.txt
```

---

# 🔑 4. Generate API Keys

---

## ⚡ GROQ API Key

### Console

[Groq Console](https://console.groq.com?utm_source=chatgpt.com)

### API Keys

[Groq API Keys](https://console.groq.com/keys?utm_source=chatgpt.com)

Example:

```env id="jlwmwm"
GROQ_API_KEY=gsk_xxxxx
```

---

## 🌲 Pinecone API Key

### Console

[Pinecone Console](https://app.pinecone.io?utm_source=chatgpt.com)

### API Key Docs

[Pinecone API Key Docs](https://docs.pinecone.io/guides/projects/manage-api-keys?utm_source=chatgpt.com)

Example:

```env id="jlwmmv"
PINECONE_API_KEY=pcsk_xxxxx
```

---

## 🎤 Whisper API Key (OpenAI)

### OpenAI Platform

[OpenAI Platform](https://platform.openai.com?utm_source=chatgpt.com)

### API Keys

[OpenAI API Keys](https://platform.openai.com/api-keys?utm_source=chatgpt.com)

Example:

```env id="jlwmhc"
WHISPER_API_KEY=sk-xxxx
```

---

## 🎧 OPTIONAL (Better Production Audio)

### Google Speech-to-Text

[Google Cloud Console](https://console.cloud.google.com?utm_source=chatgpt.com)

[Google Speech-to-Text Docs](https://cloud.google.com/speech-to-text/docs?utm_source=chatgpt.com)

---

# 🔐 5. Create `.env`

```bash id="jjlwmm"
nano .env
```

Paste:

```env id="jlwmym"
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

# 🐳 6. Start Infrastructure

```bash id="4qjlwm"
cd docker

docker compose up -d
```

Verify:

```bash id="9zjlwm"
docker ps
```

You should see:

* PostgreSQL
* Temporal
* MinIO

---

# 🪣 7. Create MinIO Bucket

Open:

```text id="4hjlwm"
http://localhost:9000
```

Login:

* username: `minio`
* password: `minio123`

Create bucket:

```text id="jlwm93"
audio-files
```

---

# 🌲 8. Pinecone Setup (2 OPTIONS)

---

# ✅ OPTION 1 — Manual Pinecone Index Creation (Recommended For You)

Open:

[Pinecone Console](https://app.pinecone.io?utm_source=chatgpt.com)

Click:

```text id="jlwmm7"
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

```text id="jlwm81"
512 dimensions
```

because your embeddings are:

```text id="jjlwm3"
text-embedding-3-small
```

which outputs:

```text id="xffffffff"
1536 dimensions
```

---

# ✅ OPTION 2 — Automatic Pinecone Index Creation (Infra-as-Code Style)

If you want automated setup instead of manual UI creation:

Run from project root:

```bash id="jlwm9y"
python -m scripts.create_pinecone_index
```

⚠️ MUST use:

```bash id="jlwmvq"
python -m
```

NOT:

```bash id="jlwm7s"
python scripts/create_pinecone_index.py
```

Otherwise you get:

```text id="jlwmzo"
ModuleNotFoundError: app
```

---

# ⚙️ 9. Fix `alembic.ini`

ROOT FILE:

```text id="3hjlwm"
AudioMind-AI/alembic.ini
```

Use:

```ini id="jlwm0n"
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

# ⚡ 10. Fix `alembic/env.py`

Replace ENTIRE file with async-safe version using:

```python id="jlwmk2"
async_engine_from_config
```

NOT:

```python id="jlwm5x"
engine_from_config
```

Otherwise:

```text id="jlwmn2"
MissingGreenlet
```

error happens.

---

# 🗄️ 11. Run Database Migrations

Back to root:

```bash id="jlwmop"
cd ..
```

Generate migration:

```bash id="6djlwm"
alembic revision --autogenerate -m "init"
```

Apply migration:

```bash id="8fjlwm"
alembic upgrade head
```

---

# ⚡ 12. Start Temporal Worker

NEW TERMINAL:

```bash id="jlwm5m"
source venv/bin/activate
```

Run:

```bash id="4jjlwm"
python -m app.workflows.worker
```

---

# 🚀 13. Start FastAPI App

NEW TERMINAL:

```bash id="4gjlwm"
source venv/bin/activate
```

Run:

```bash id="q4jlwm"
uvicorn app.main:app --reload
```

Expected:

```text id="z3jlwm"
Running on http://127.0.0.1:8000
```

---

# 📘 14. Open Swagger

Open:

```text id="2djlwm"
http://localhost:8000/docs
```

---

# 🔐 15. Generate JWT Token

```python id="jlwm4n"
from app.core.security import create_access_token

token = create_access_token({"sub": "user-123"})
print(token)
```

---

# 🎤 16. Upload Audio

```http id="7rjlwm"
POST /upload
```

Header:

```text id="jlwmys"
Authorization: Bearer YOUR_TOKEN
```

Upload `.wav`.

---

# 🔄 17. Verify Worker Processing

Worker logs should show:

* transcription
* chunking
* embeddings
* Pinecone upsert

---

# 🔎 18. Query Audio

```http id="4ljlwm"
POST /query
```

Body:

```json id="9mjlwm"
{
  "query": "What did I say about AI?"
}
```

---

# 🚨 Common Errors

---

## ❌ MissingGreenlet

Cause:

* sync Alembic engine with async DB

Fix:

```python id="jlwmxv"
async_engine_from_config
```

---

## ❌ Pinecone Dimension Mismatch

Cause:

```text id="n3jlwm"
Index = 512
Embedding = 1536
```

Fix:

* recreate Pinecone index with `1536`

---

## ❌ ModuleNotFoundError: app

Cause:

```bash id="t6jlwm"
python scripts/file.py
```

Fix:

```bash id="5tjlwm"
python -m scripts.file
```

---

## ❌ Worker not processing

Cause:

* Temporal worker not running

Fix:

```bash id="9qjlwm"
python -m app.workflows.worker
```

---

# 🧠 FINAL Correct Startup Sequence

```text id="t4jlwm"
1. docker compose up -d
2. create Pinecone index (1536 dim)
3. alembic revision --autogenerate -m "init"
4. alembic upgrade head
5. python -m app.workflows.worker
6. uvicorn app.main:app --reload
```
