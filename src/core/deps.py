from fastapi import Query, HTTPException, Depends
from src.core.jwt import decode_jwt_token
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_db
from src.schemas.users import UserRead
from src.services.users import UserService


class Pagination:
    def __init__(
        self, limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)
    ):
        self.limit = limit
        self.offset = offset


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> UserRead:
    try:
        payload = await decode_jwt_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
            )
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
        )
    user_id = int(user_id)
    user = await UserService.get_user_by_id(db, user_id)
    if user.deleted_at is not None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return user


async def dev_get_current_user(
    user_id: int, db: AsyncSession = Depends(get_db)
) -> UserRead:
    user = await UserService.get_user_by_id(db, user_id)
    if user.deleted_at is not None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return user


async def verify_admin(user: UserRead = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return user


async def dev_verify_admin(user: UserRead = Depends(dev_get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return user
