from fastapi import APIRouter, Depends, Request
from starlette.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from src.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.users import UserRead
from src.schemas.auth import UserLogin, UserCreate
from src.services.auth import AuthService
import json


auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/registration", response_model=UserRead, status_code=201)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)) -> UserRead:
    return await AuthService.user_registration(db, user)


@auth_router.post("/login")
async def login_user(
    user: UserLogin, db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    return await AuthService.user_login(db, user)


@auth_router.post("/token")
async def get_token_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
) -> dict:
    user = UserLogin(login=form_data.username, password=form_data.password)
    login_response: JSONResponse = await AuthService.user_login(db, user)
    content = login_response.body.decode()
    content_dict = json.loads(content)
    access_token = content_dict["data"]["access_token"]

    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.post("/refresh")
async def refresh(request: Request, db: AsyncSession = Depends(get_db)) -> JSONResponse:
    return await AuthService.refresh(db, request)
