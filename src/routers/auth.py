from fastapi import APIRouter, Depends, Request
from starlette.responses import JSONResponse

from src.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.users import UserRead
from src.schemas.auth import UserLogin, UserCreate
from src.schemas.dto import ApiResponse
from src.services.auth import AuthService


auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post(
    "/registration", response_model=ApiResponse[UserRead], status_code=201
)
async def create_user(
    user: UserCreate, db: AsyncSession = Depends(get_db)
) -> ApiResponse[UserRead]:
    return await AuthService.user_registration(db, user)


@auth_router.post("/login")
async def login_user(
    user: UserLogin, db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    return await AuthService.user_login(db, user)


@auth_router.post("/refresh")
async def refresh(request: Request, db: AsyncSession = Depends(get_db)) -> JSONResponse:
    return await AuthService.refresh(db, request)
