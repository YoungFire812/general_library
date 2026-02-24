from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.users import UserRead
from src.schemas.auth import UserLogin, UserCreate, AuthResponse
from src.schemas.dto import ApiResponse
from src.models.models import User, Cart
from src.core.security import hash_password
from sqlalchemy.exc import IntegrityError
from src.core.sqlErrors import UNIQUE_VIOLATION, is_error
from sqlalchemy import select
from src.core.security import verify_password
from src.core.jwt import create_access_token, create_refresh_token, decode_refresh_token
from fastapi.responses import JSONResponse
from jose import JWTError
from src.services.users import UserService


class AuthService:
    @staticmethod
    async def user_registration(
        db: AsyncSession, data: UserCreate
    ) -> ApiResponse[UserRead]:
        hashed_password = hash_password(data.password)
        user_dict = data.model_dump(exclude={"password"})
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
    async def user_login(db: AsyncSession, data: UserLogin) -> JSONResponse:
        result = await db.execute(
            select(User).where(
                (User.email == data.login) | (User.username == data.login)
            )
        )
        db_user = result.scalar_one_or_none()

        if not db_user or not verify_password(data.password, db_user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = create_access_token({"sub": str(db_user.id)})
        refresh_token = create_refresh_token({"sub": str(db_user.id)})

        auth_response = AuthResponse(
            access_token=access_token,
            user=UserRead.model_validate(db_user, from_attributes=True),
        )

        response = JSONResponse(
            content=ApiResponse(
                message="Login success!", data=auth_response
            ).model_dump()
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
        )

        return response

    @staticmethod
    async def refresh(db: AsyncSession, request: Request) -> JSONResponse:
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            raise HTTPException(status_code=401, detail="Missing refresh token")

        try:
            payload = decode_refresh_token(refresh_token)
            user_id = int(payload.get("sub"))
            user_data = await UserService.get_user(db, user_id)
            user = user_data.data
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        new_access = create_access_token({"sub": user_id})
        new_refresh = create_refresh_token({"sub": user_id})

        auth_response = AuthResponse(
            access_token=new_access,
            user=UserRead.model_validate(user, from_attributes=True),
        )

        response = JSONResponse(
            content=ApiResponse(
                message="Token refreshed", data=auth_response
            ).model_dump()
        )
        response.set_cookie(
            key="refresh_token",
            value=new_refresh,
            httponly=True,
            secure=True,
            samesite="lax",
        )

        return response
