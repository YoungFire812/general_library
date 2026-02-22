from fastapi import APIRouter, Depends
from src.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.users import UserRead, UserCreate, UserUpdate
from src.schemas.dto import ApiResponse
from src.services.users import UserService


users_router = APIRouter(prefix="/users", tags=["Users"])


@users_router.get("/{user_id}", response_model=ApiResponse[UserRead])
async def get_user(
    user_id: int, db: AsyncSession = Depends(get_db)
) -> ApiResponse[UserRead]:
    return await UserService.get_user(db, user_id)


@users_router.post("/", response_model=ApiResponse[UserRead], status_code=201)
async def create_user(
    user: UserCreate, db: AsyncSession = Depends(get_db)
) -> ApiResponse[UserRead]:
    return await UserService.create_user(db, user)


@users_router.patch("/{user_id}", response_model=ApiResponse[UserRead])
async def update_user(
    user_id: int, data: UserUpdate, db: AsyncSession = Depends(get_db)
) -> ApiResponse[UserRead]:
    return await UserService.update_user(db, user_id, data)
