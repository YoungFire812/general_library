from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.users import UserRead
from src.schemas.auth import UserLogin, UserCreate, AuthResponse
from src.models.models import User, Cart
from src.core.security import hash_password
from sqlalchemy.exc import IntegrityError
from src.core.sqlErrors import UNIQUE_VIOLATION, is_error
from sqlalchemy import select
from src.core.security import verify_password
from src.core.jwt import create_access_token, create_refresh_token, decode_jwt_token
from fastapi.responses import JSONResponse
from jose import JWTError
from src.services.users import UserService
from loguru import logger


class AuthService:
    @staticmethod
    async def user_registration(db: AsyncSession, data: UserCreate) -> UserRead:
        hashed_password = await hash_password(data.password)
        user_dict = data.model_dump(exclude={"password"})
        user_dict["password"] = hashed_password

        db_user = User(**user_dict)
        db_user.carts = Cart()
        db.add(db_user)

        await db.flush()
        await db.refresh(db_user)

        logger.info("User registered successfully", email=db_user.email)
        return UserRead.model_validate(db_user)

    @staticmethod
    async def user_login(db: AsyncSession, data: UserLogin) -> JSONResponse:
        result = await db.execute(
            select(User).where(
                (User.email == data.login) | (User.username == data.login)
            )
        )
        db_user = result.scalar_one_or_none()

        if (
            not db_user
            or not await verify_password(data.password, db_user.password)
            or db_user.deleted_at is not None
        ):
            logger.warning("Failed login attempt", login=data.login)
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = await create_access_token({"sub": str(db_user.id)})
        refresh_token = await create_refresh_token({"sub": str(db_user.id)})

        auth_response = AuthResponse(
            access_token=access_token,
            user=UserRead.model_validate(db_user, from_attributes=True),
        )

        response = JSONResponse(
            content={"message": "Login success!", "data": auth_response.model_dump(mode="json")}
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
        )

        logger.info("User logged in successfully", user_id=db_user.id, email=db_user.email)
        return response

    @staticmethod
    async def refresh(db: AsyncSession, request: Request) -> JSONResponse:
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            logger.warning("Refresh token missing")
            raise HTTPException(status_code=401, detail="Missing refresh token")

        try:
            payload = await decode_jwt_token(refresh_token)
            user_id = int(payload.get("sub"))
            user = await UserService.get_user_by_id(db, user_id)
        except JWTError:
            logger.warning("Invalid refresh token")
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        new_access = await create_access_token({"sub": user_id})
        new_refresh = await create_refresh_token({"sub": user_id})

        auth_response = AuthResponse(
            access_token=new_access,
            user=user
        )

        response = JSONResponse(
            content={"message": "Token refreshed", "data": auth_response.model_dump(mode="json")}
        )
        response.set_cookie(
            key="refresh_token",
            value=new_refresh,
            httponly=True,
            secure=True,
            samesite="lax",
        )

        logger.info("Access and refresh tokens issued", user_id=user_id)
        return response
