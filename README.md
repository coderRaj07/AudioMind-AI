# 🚀 FINAL Correct Run Instructions (Async SQLAlchemy + Alembic + Temporal)

---

# ✅ 1. Correct Project Structure

You should have ONLY this:

```text id="7fjlwm"
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
│
├── .env
├── alembic.ini
├── requirements.txt
```

---

# 🚨 IMPORTANT FIX

DELETE these if they exist:

```bash id="jlwmv7"
rm -rf docker/alembic
rm -f docker/alembic.ini
```

You accidentally initialized Alembic inside docker earlier.

---

# ✅ 2. Activate Virtual Environment

From project root:

```bash id="jlwm0o"
source venv/bin/activate
```

---

# ✅ 3. Install Dependencies

```bash id="jlwmmf"
pip install --upgrade pip setuptools wheel

pip install -r requirements.txt
```

---

# ✅ 4. Verify `.env`

Project root:

```env id="jlwm0m"
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/voice_rag
```

⚠️ MUST use:

```text id="jlwm2y"
postgresql+asyncpg://
```

NOT:

```text id="jlwmca"
postgresql://
```

---

# ✅ 5. FIX `alembic.ini`

ROOT FILE:

```text id="jlwmho"
AudioMind-AI/alembic.ini
```

Use:

```ini id="jlwmv1"
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

# ✅ 6. FIX `alembic/env.py` (CRITICAL)

Replace ENTIRE file with this:

```python id="jlwmfs"
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from app.db.base import Base
from app.db import models
from app.core.config import get_settings

settings = get_settings()

config = context.config

config.set_main_option(
    "sqlalchemy.url",
    settings.DATABASE_URL
)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online():
    import asyncio
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

---

# ✅ 7. Start Infrastructure

Go into docker folder:

```bash id="jlwmuh"
cd docker
```

Run:

```bash id="jlwmww"
docker compose up -d
```

Verify:

```bash id="jlwm0j"
docker ps
```

You should see:

* PostgreSQL
* Temporal
* MinIO

---

# ✅ 8. Create MinIO Bucket

Open:

```text id="jlwm13"
http://localhost:9000
```

Login:

* username: `minio`
* password: `minio123`

Create bucket:

```text id="jlwmjs"
audio-files
```

---

# ✅ 9. Run Alembic Migration (FIXED FLOW)

Go back to root:

```bash id="jlwmv8"
cd ..
```

---

## Generate migration

```bash id="jlwm7l"
alembic revision --autogenerate -m "init"
```

Expected:

```text id="jlwm3w"
Generating alembic/versions/xxxx_init.py
```

---

## Apply migration

```bash id="jlwm2n"
alembic upgrade head
```

Expected:

```text id="jlwmvq"
Running upgrade -> xxxx
```

---

# ✅ 10. Create Pinecone Index

```bash id="jlwmqv"
python scripts/create_pinecone_index.py
```

---

# ✅ 11. Start Temporal Worker

NEW TERMINAL:

```bash id="jlwmkg"
source venv/bin/activate
```

Run:

```bash id="jlwm7d"
python -m app.workflows.worker
```

---

# ✅ 12. Start FastAPI App

NEW TERMINAL:

```bash id="jlwmtt"
source venv/bin/activate
```

Run:

```bash id="jlwmz4"
uvicorn app.main:app --reload
```

---

# ✅ 13. Open Swagger

Open:

```text id="jlwmh3"
http://localhost:8000/docs
```

---

# ✅ 14. Generate JWT Token

Run:

```python id="jlwmhh"
from app.core.security import create_access_token

token = create_access_token({"sub": "user-123"})
print(token)
```

---

# ✅ 15. Test Upload

Use:

```http id="jlwm8o"
POST /upload
```

Header:

```text id="jlwmig"
Authorization: Bearer YOUR_TOKEN
```

Upload `.wav`.

---

# ✅ 16. Verify Processing

Worker logs should show:

* transcription
* embeddings
* Pinecone upsert

---

# ✅ 17. Query Audio

```http id="jlwm7g"
POST /query
```

Body:

```json id="jlwm6k"
{
  "query": "What did I say about AI?"
}
```

---

# 🚨 IMPORTANT Runtime Notes

## If migration fails again

Usually one of:

### ❌ Wrong DB URL

Must be:

```text id="jlwmh9"
postgresql+asyncpg://
```

---

### ❌ PostgreSQL container not running

Check:

```bash id="jlwm0s"
docker ps
```

---

### ❌ Models not imported

Ensure:

```python id="jlwmmh"
from app.db import models
```

exists in `alembic/env.py`

---

# 🧠 FINAL Correct Startup Sequence

```text id="jlwm0y"
1. docker compose up -d
2. alembic revision --autogenerate -m "init"
3. alembic upgrade head
4. python scripts/create_pinecone_index.py
5. python -m app.workflows.worker
6. uvicorn app.main:app --reload
```
