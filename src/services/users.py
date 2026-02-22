from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.users import UserUpdate, UserRead, UserCreate
from src.schemas.dto import ApiResponse
from src.models.models import User, Cart
from src.core.security import hash_password
from sqlalchemy.exc import IntegrityError
from src.core.sqlErrors import UNIQUE_VIOLATION, is_error


class UserService:
    @staticmethod
    async def get_user(db: AsyncSession, user_id: int):
        pass

    @staticmethod
    async def create_user(db: AsyncSession, user: UserCreate) -> ApiResponse[UserRead]:
        hashed_password = hash_password(user.password)
        user_dict = user.model_dump(exclude={"password"})
        user_dict["password"] = hashed_password

        db_user = User(**user_dict)
        db_user.carts = Cart(items_count=0)
        db.add(db_user)

        try:
            await db.commit()
            await db.refresh(db_user)

            return ApiResponse(
                message="User created!",
                data=UserRead.model_validate(db_user, from_attributes=True),
            )

        except IntegrityError as e:
            await db.rollback()
            if is_error(e, UNIQUE_VIOLATION):
                raise HTTPException(
                    status_code=409, detail="User with this data is already registered"
                )
            else:
                raise

    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, data: UserUpdate):
        pass
