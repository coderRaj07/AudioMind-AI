import httpx

from app.core.config import get_settings
from app.core.logger import get_logger
from app.utils.retry import retry_policy

settings = get_settings()
logger = get_logger(__name__)


@retry_policy(5)
async def generate_embeddings(texts):

    url = "https://api.jina.ai/v1/embeddings"

    headers = {
        "Authorization": f"Bearer {settings.JINA_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": settings.JINA_EMBEDDING_MODEL,
        "input": texts
    }

    async with httpx.AsyncClient(timeout=60) as client:

        res = await client.post(
            url,
            json=payload,
            headers=headers
        )

    if res.status_code != 200:
        raise Exception(
            f"Jina embedding failed: {res.status_code} {res.text}"
        )

    data = res.json()["data"]

    return [item["embedding"] for item in data]