from sqlalchemy import select
from app.db.models.user import User
from app.db.repositories.base import BaseRepository


class UserRepository(BaseRepository):

    async def get_by_email(self, email: str):
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def create(self, email: str):
        user = User(email=email)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
