from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException
from app.db.repositories.user_repo import UserRepository

security = HTTPBearer(auto_error=False, bearerFormat="JWT")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    if not credentials or credentials.scheme.lower() != "bearer":
        raise UnauthorizedException("Invalid auth header")

    token = credentials.credentials.strip().strip('"').strip("'")
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
