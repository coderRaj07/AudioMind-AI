from uuid import UUID

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException
from app.db.repositories.user_repo import UserRepository


async def get_current_user(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedException("Invalid auth header")

    token = authorization.split(" ")[1]
    payload = decode_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid token")

    try:
        parsed_user_id = UUID(user_id)
    except ValueError:
        raise UnauthorizedException("Invalid token")

    user = await UserRepository(db).get_by_id(parsed_user_id)
    if not user:
        raise UnauthorizedException("User not found")

    return user


async def get_db_session(db: AsyncSession = Depends(get_db)):
    return db
