from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from temporalio.client import Client

from app.schemas.audio import UploadResponse
from app.api.deps import get_current_user, get_db_session
from app.services.s3_service import upload_file
from app.db.repositories.audio_repo import AudioRepository
from app.core.config import get_settings
from app.utils.ids import generate_uuid

router = APIRouter()
settings = get_settings()




@router.post("/upload", response_model=UploadResponse)
async def upload_audio(
    file: UploadFile = File(...),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    file_bytes = await file.read()

    file_key = f"{user.id}/{generate_uuid()}.wav"

    # Upload to S3
    file_url = upload_file(file_bytes, file_key)

    # Store DB
    audio_repo = AudioRepository(db)
    audio = await audio_repo.create(user.id, file_url)
    audio_id = audio.id

    # Trigger Temporal
    client = await Client.connect(settings.TEMPORAL_HOST)

    await client.start_workflow(
        "AudioIngestionWorkflow",
        {
            "user_id": str(user.id),
            "audio_id": str(audio_id),
            "file_key": file_key,
        },
        id=f"audio-{audio_id}",
        task_queue=settings.TASK_QUEUE,
    )

    return UploadResponse(
        audio_id=audio_id,
        status="processing"
    )
