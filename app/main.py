from fastapi import FastAPI
from app.core.config import get_settings
from app.api import upload, query, health

settings = get_settings()

app = FastAPI(title=settings.APP_NAME)

app.include_router(upload.router)
app.include_router(query.router)
app.include_router(health.router)