from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.users import UserUpdate, UserRead
from src.models.models import User
from sqlalchemy import select
from src.schemas.dto import ApiResponse
from datetime import datetime, timezone
from src.core.security import hash_password
from src.core.sqlErrors import UNIQUE_VIOLATION, is_error
from sqlalchemy.exc import IntegrityError


class UserService:
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> UserRead:
        result = await db.execute(select(User).where(User.id == user_id, User.deleted_at.is_(None)))

        db_user = result.scalar_one_or_none()
        if db_user is None:
            raise HTTPException(
                status_code=404, detail=f"User with id {user_id} not found!"
            )

        return UserRead.model_validate(db_user)

    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, data: UserUpdate):
        result = await db.execute(
            select(User).where(
                (User.id == user_id) & (User.deleted_at.is_(None))
            )
        )

        db_user = result.scalar_one_or_none()
        if db_user is None:
            raise HTTPException(404, "User not found")

        if data.password is not None:
            hashed_password = hash_password(data.password)
            data = data.model_dump(exclude={"password"})
            data["password"] = hashed_password
        else:
            data = data.model_dump()

        if not data:
            raise HTTPException(400, "No fields to update")

        for field, value in data.items():
            if value is not None:
                setattr(db_user, field, value)

        try:
            await db.commit()
            await db.refresh(db_user)
            return UserRead.model_validate(db_user)
        except IntegrityError as e:
            await db.rollback()
            if is_error(e, UNIQUE_VIOLATION):
                raise HTTPException(
                    status_code=409, detail="User with this data already exists"
                )
            else:
                raise


    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int):
        result = await db.execute(
            select(User).where(
                (User.id == user_id) & (User.deleted_at.is_(None))
            )
        )

        db_user = result.scalar_one_or_none()
        if db_user is None:
            raise HTTPException(404, "User not found!")

        db_user.deleted_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(db_user)

