import asyncio
from temporalio.worker import Worker
from temporalio.client import Client

from app.core.config import get_settings
from app.workflows.audio_workflow import AudioIngestionWorkflow
from app.workflows.activities import process_audio_activity

settings = get_settings()


async def main():
    client = await Client.connect(settings.TEMPORAL_HOST)

    worker = Worker(
        client,
        task_queue=settings.TASK_QUEUE,
        workflows=[AudioIngestionWorkflow],
        activities=[process_audio_activity],
    )

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())