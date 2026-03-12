from fastapi import APIRouter, Depends
from src.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.users import UserRead, UserUpdate
from src.schemas.dto import ApiResponse
from src.services.users import UserService
from src.core.deps import dev_get_current_user


users_router = APIRouter(prefix="/users", tags=["Users"])


@users_router.get("/{user_id}", response_model=UserRead)
async def get_user_by_id(
    user_id: int, db: AsyncSession = Depends(get_db)
) -> UserRead:
    return await UserService.get_user_by_id(db, user_id)


@users_router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    data: UserUpdate, db: AsyncSession = Depends(get_db), user: UserRead = Depends(dev_get_current_user)
) -> UserRead:
    return await UserService.update_user(db, user.id, data)


@users_router.delete("/{user_id}", status_code=204)
async def delete_user(
    user: UserRead = Depends(dev_get_current_user), db: AsyncSession = Depends(get_db)
):
    await UserService.delete_user(db, user.id)