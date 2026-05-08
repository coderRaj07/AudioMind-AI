from uuid import UUID

from fastapi import Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException
from app.db.repositories.user_repo import UserRepository

security = APIKeyHeader(
    name="Authorization",
    auto_error=False,
    description="Send JWT token only, without the Bearer prefix. Example: eyJhbGciOiJIUzI1NiIs...",
)


async def get_current_user(
    authorization: str | None = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    if not authorization:
        raise UnauthorizedException("Invalid auth header")

    if authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]
    else:
        token = authorization

    token = token.strip().strip('"').strip("'")
    if not token:
        raise UnauthorizedException("Invalid auth header")

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
