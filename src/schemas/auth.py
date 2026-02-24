from pydantic import BaseModel, Field, EmailStr
from src.schemas.users import UserRead


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class UserLogin(BaseModel):
    login: str = Field(max_length=100)
    password: str = Field(min_length=8, max_length=128)


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=25)
    email: EmailStr = Field(max_length=100)
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=35)
