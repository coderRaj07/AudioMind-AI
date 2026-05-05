import httpx
from app.core.config import get_settings
from app.core.logger import get_logger
from app.utils.retry import retry_policy

settings = get_settings()
logger = get_logger(__name__)


@retry_policy(3)
async def transcribe_audio(file_bytes: bytes) -> dict:
    url = "https://api.openai.com/v1/audio/transcriptions"

    headers = {
        "Authorization": f"Bearer {settings.WHISPER_API_KEY}"
    }

    files = {
        "file": ("audio.wav", file_bytes),
        "model": (None, "whisper-1"),
    }

    async with httpx.AsyncClient(timeout=600) as client:
        response = await client.post(url, headers=headers, files=files)

    if response.status_code != 200:
        logger.error(f"Whisper failed: {response.text}")
        raise Exception("Transcription failed")

    return response.json()