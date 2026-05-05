from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from temporalio.client import Client

from app.api.deps import get_current_user, get_db_session
from app.services.s3_service import upload_file
from app.db.crud import create_audio
from app.core.config import get_settings
from app.utils.ids import generate_uuid

router = APIRouter()
settings = get_settings()


@router.post("/upload")
async def upload_audio(
    file: UploadFile = File(...),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    file_bytes = await file.read()

    file_key = f"{user['user_id']}/{generate_uuid()}.wav"

    # Upload to S3
    file_url = upload_file(file_bytes, file_key)

    # Store DB
    audio_id = await create_audio(db, user["user_id"], file_url)

    # Trigger Temporal
    client = await Client.connect(settings.TEMPORAL_HOST)

    await client.start_workflow(
        "AudioIngestionWorkflow",
        {
            "user_id": user["user_id"],
            "audio_id": str(audio_id),
            "file_key": file_key,
        },
        id=f"audio-{audio_id}",
        task_queue=settings.TASK_QUEUE,
    )

    return {
        "audio_id": str(audio_id),
        "status": "processing"
    }