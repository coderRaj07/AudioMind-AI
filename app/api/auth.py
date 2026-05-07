from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.core.exceptions import BadRequestException, UnauthorizedException
from app.core.security import create_access_token, hash_password, verify_password
from app.db.repositories.user_repo import UserRepository
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: UserCreate,
    db: AsyncSession = Depends(get_db_session),
):
    email = body.email.strip().lower()
    user_repo = UserRepository(db)

    existing_user = await user_repo.get_by_email(email)
    if existing_user:
        raise BadRequestException("Email already registered")

    user = await user_repo.create(
        email=email,
        password_hash=hash_password(body.password),
    )
    token = create_access_token({"sub": str(user.id)})

    return TokenResponse(access_token=token, user=user)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: UserLogin,
    db: AsyncSession = Depends(get_db_session),
):
    email = body.email.strip().lower()
    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(email)

    if not user or not user.password_hash:
        raise UnauthorizedException("Invalid email or password")

    if not verify_password(body.password, user.password_hash):
        raise UnauthorizedException("Invalid email or password")

    token = create_access_token({"sub": str(user.id)})

    return TokenResponse(access_token=token, user=user)


@router.get("/me", response_model=UserResponse)
async def read_me(user=Depends(get_current_user)):
    return user
