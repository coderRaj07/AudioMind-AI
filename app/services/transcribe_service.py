import httpx

from app.core.config import get_settings
from app.core.logger import get_logger
from app.utils.retry import retry_policy

settings = get_settings()
logger = get_logger(__name__)


@retry_policy(3)
async def transcribe_audio(file_bytes: bytes) -> dict:
    url = "https://api.deepgram.com/v1/listen"

    headers = {
        "Authorization": f"Token {settings.DEEPGRAM_API_KEY}",
        "Content-Type": "audio/wav",
    }

    params = {
        "model": "nova-2",
        "smart_format": "true",
        "punctuate": "true",
    }

    async with httpx.AsyncClient(timeout=600) as client:
        response = await client.post(
            url,
            headers=headers,
            params=params,
            content=file_bytes,
        )

    if response.status_code != 200:
        logger.error(f"Deepgram failed: {response.text}")
        raise Exception("Transcription failed")

    data = response.json()

    try:
        transcript = (
            data["results"]["channels"][0]["alternatives"][0]["transcript"]
        )

        return {
            "text": transcript
        }

    except Exception as e:
        logger.error(f"Deepgram parse failed: {e}")
        raise Exception("Invalid transcription response")