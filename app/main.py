from fastapi import FastAPI
from app.core.config import get_settings
from app.core.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

app = FastAPI(title=settings.APP_NAME)


@app.get("/health")
async def health():
    return {"status": "ok"}