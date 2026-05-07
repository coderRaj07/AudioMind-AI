from sqlalchemy import select
from app.db.models.user import User
from app.db.repositories.base import BaseRepository


class UserRepository(BaseRepository):

    async def get_by_id(self, user_id):
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str):
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def create(self, email: str, password_hash: str | None = None):
        user = User(email=email, password_hash=password_hash)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
