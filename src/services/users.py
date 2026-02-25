from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.users import UserUpdate, UserRead
from src.models.models import User
from sqlalchemy import select
from src.schemas.dto import ApiResponse


class UserService:
    @staticmethod
    async def get_user(db: AsyncSession, user_id: int) -> ApiResponse[UserRead]:
        result = await db.execute(select(User).where(User.id == user_id))

        db_user = result.scalar_one_or_none()
        if db_user is None:
            raise HTTPException(
                status_code=404, detail=f"User with id {user_id} not found!"
            )

        return ApiResponse(
            message=f"Data for user {user_id}",
            data=UserRead.model_validate(db_user),
        )

    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, data: UserUpdate):
        pass
