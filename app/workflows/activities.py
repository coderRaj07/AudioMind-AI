from temporalio import activity
from app.services.whisper_service import transcribe_audio
from app.services.embedding_service import generate_embeddings
from app.services.pinecone_service import upsert_vectors
from app.ingestion.chunking import chunk_text
from app.ingestion.cleaner import clean_transcript
from app.services.s3_service import download_file
from app.utils.ids import generate_uuid


@activity.defn
async def process_audio_activity(input_data: dict):
    user_id = input_data["user_id"]
    audio_id = input_data["audio_id"]
    file_key = input_data["file_key"]

    # 1. Download
    file_bytes = download_file(file_key)

    # 2. Transcribe
    transcript = await transcribe_audio(file_bytes)
    text = clean_transcript(transcript.get("text", ""))

    # 3. Chunk
    chunks = chunk_text(text)

    # 4. Embed
    texts = [c["text"] for c in chunks]
    embeddings = await generate_embeddings(texts)

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

    return {"status": "completed", "chunks": len(vectors)}