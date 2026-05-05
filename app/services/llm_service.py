import httpx
from app.core.config import get_settings
from app.core.logger import get_logger
from app.utils.retry import retry_policy

settings = get_settings()
logger = get_logger(__name__)


async def _call_groq(prompt: str):
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}"
    }

    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    async with httpx.AsyncClient(timeout=60) as client:
        res = await client.post(url, json=payload, headers=headers)

    if res.status_code != 200:
        raise Exception(f"Groq failed: {res.text}")

    return res.json()["choices"][0]["message"]["content"]


async def _call_cerebras(prompt: str):
    url = "https://api.cerebras.ai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {settings.CEREBRAS_API_KEY}"
    }

    payload = {
        "model": "llama3-70b",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    async with httpx.AsyncClient(timeout=60) as client:
        res = await client.post(url, json=payload, headers=headers)

    if res.status_code != 200:
        raise Exception(f"Cerebras failed: {res.text}")

    return res.json()["choices"][0]["message"]["content"]


@retry_policy(3)
async def generate_answer(prompt: str):
    try:
        return await _call_groq(prompt)
    except Exception as e:
        logger.warning(f"Groq failed, fallback to Cerebras: {e}")
        return await _call_cerebras(prompt)