import httpx
from app.core.config import get_settings
from app.core.logger import get_logger
from app.utils.retry import retry_policy

settings = get_settings()
logger = get_logger(__name__)


async def _embed_with_groq(texts):
    url = "https://api.groq.com/openai/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}"
    }

    payload = {
        "model": "text-embedding-3-small",
        "input": texts
    }

    async with httpx.AsyncClient(timeout=60) as client:
        res = await client.post(url, json=payload, headers=headers)

    if res.status_code != 200:
        raise Exception("Groq embedding failed")

    return [d["embedding"] for d in res.json()["data"]]


async def _embed_with_cerebras(texts):
    url = "https://api.cerebras.ai/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {settings.CEREBRAS_API_KEY}"
    }

    payload = {
        "model": "text-embedding-3-small",
        "input": texts
    }

    async with httpx.AsyncClient(timeout=60) as client:
        res = await client.post(url, json=payload, headers=headers)

    if res.status_code != 200:
        raise Exception("Cerebras embedding failed")

    return [d["embedding"] for d in res.json()["data"]]


@retry_policy(5)
async def generate_embeddings(texts):
    try:
        return await _embed_with_groq(texts)
    except Exception as e:
        logger.warning(f"Groq failed, fallback to Cerebras: {e}")
        return await _embed_with_cerebras(texts)