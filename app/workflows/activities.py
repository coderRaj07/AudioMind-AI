from temporalio import activity
from app.services.transcribe_service import transcribe_audio
from app.services.embedding_service import generate_embeddings
from app.services.pinecone_service import upsert_vectors
from app.ingestion.chunking import chunk_text
from app.ingestion.cleaner import clean_transcript
from app.services.s3_service import download_file
from app.utils.ids import generate_uuid
from app.db.session import AsyncSessionLocal
from app.db.repositories.audio_repo import AudioRepository


async def _set_audio_status(audio_id: str, status: str, progress: float | None = None):
    async with AsyncSessionLocal() as session:
        repo = AudioRepository(session)
        await repo.update_status(audio_id, status, progress)


@activity.defn
async def process_audio_activity(input_data: dict):
    user_id = input_data["user_id"]
    audio_id = input_data["audio_id"]
    file_key = input_data["file_key"]

    try:
        await _set_audio_status(audio_id, "processing", 10.0)

        # 1. Download
        file_bytes = download_file(file_key)
        await _set_audio_status(audio_id, "processing", 25.0)

        # 2. Transcribe
        transcript = await transcribe_audio(file_bytes)
        text = clean_transcript(transcript.get("text", ""))
        await _set_audio_status(audio_id, "processing", 45.0)

        # 3. Chunk
        chunks = chunk_text(text)
        await _set_audio_status(audio_id, "processing", 65.0)

        # 4. Embed
        texts = [c["text"] for c in chunks]
        embeddings = await generate_embeddings(texts)
        await _set_audio_status(audio_id, "processing", 85.0)

        # 5. Prepare Pinecone vectors
        vectors = []
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            vectors.append({
                "id": generate_uuid(),
                "values": emb,
                "metadata": {
                    "user_id": user_id,
                    "audio_id": audio_id,
                    "text": chunk["text"],
                    "start_time": chunk["start_time"],
                    "end_time": chunk["end_time"],
                }
            })

        # 6. Store
        upsert_vectors(vectors)
        await _set_audio_status(audio_id, "completed", 100.0)

        return {"status": "completed", "chunks": len(vectors)}
    except Exception:
        await _set_audio_status(audio_id, "failed", 0.0)
        raise
