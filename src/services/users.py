from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.users import UserUpdate, UserRead
from src.models.models import User
from sqlalchemy import select
from datetime import datetime, timezone
from src.core.security import hash_password
from loguru import logger


class UserService:
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> UserRead:
        result = await db.execute(
            select(User).where(User.id == user_id, User.deleted_at.is_(None))
        )

        db_user = result.scalar_one_or_none()
        if db_user is None:
            logger.warning("User not found")
            raise HTTPException(status_code=404, detail=f"User with id {user_id} not found!")

        logger.info("User fetched successfully")
        return UserRead.model_validate(db_user)

    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, data: UserUpdate):
        result = await db.execute(
            select(User).where((User.id == user_id) & (User.deleted_at.is_(None)))
        )

        db_user = result.scalar_one_or_none()
        if db_user is None:
            logger.warning("User not found for update")
            raise HTTPException(404, "User not found")

        if data.password is not None:
            hashed_password = await hash_password(data.password)
            data = data.model_dump(exclude={"password"})
            data["password"] = hashed_password
        else:
            data = data.model_dump()

        if not data:
            logger.warning("No fields to update")
            raise HTTPException(400, "No fields to update")

        for field, value in data.items():
            if value is not None:
                setattr(db_user, field, value)

        await db.commit()
        await db.refresh(db_user)

        logger.info("User updated successfully", updated_fields=list(data_dict.keys()))
        return UserRead.model_validate(db_user)


    @staticmethod
    async def delete_user(db: AsyncSession, user: UserRead):
        result = await db.execute(
            select(User).where((User.id == user.id), (User.deleted_at.is_(None)))
        )

        db_user = result.scalar_one_or_none()
        if db_user is None:
            logger.warning("User not found for delete")
            raise HTTPException(404, "User not found!")

        db_user.deleted_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(db_user)

        logger.info("User soft-deleted successfully")
