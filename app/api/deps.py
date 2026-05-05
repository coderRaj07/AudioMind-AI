from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException


async def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise UnauthorizedException("Invalid auth header")

    token = authorization.split(" ")[1]
    payload = decode_token(token)

    return {"user_id": payload.get("sub")}


async def get_db_session(db: AsyncSession = Depends(get_db)):
    return db