from sqlalchemy import select, update
from app.db.models.audio import Audio
from app.db.repositories.base import BaseRepository


class AudioRepository(BaseRepository):

    async def create(self, user_id: str, file_url: str):
        audio = Audio(
            user_id=user_id,
            file_url=file_url,
            status="processing"
        )
        self.db.add(audio)
        await self.db.commit()
        await self.db.refresh(audio)
        return audio

    async def update_status(self, audio_id: str, status: str):
        await self.db.execute(
            update(Audio)
            .where(Audio.id == audio_id)
            .values(status=status)
        )
        await self.db.commit()

    async def get_by_id(self, audio_id: str):
        result = await self.db.execute(
            select(Audio).where(Audio.id == audio_id)
        )
        return result.scalar_one_or_none()
