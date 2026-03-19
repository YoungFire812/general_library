from pydantic import BaseModel, ConfigDict, Field, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    user = "user"


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=25)
    email: EmailStr = Field(max_length=100)
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=35)


class UserRead(BaseModel):
    id: int
    username: str = Field(min_length=1, max_length=25)
    email: EmailStr = Field(max_length=100)
    full_name: str = Field(min_length=1, max_length=35)
    deleted_at: datetime | None = None
    role: UserRole
    created_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=1, max_length=25)
    email: Optional[EmailStr] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=8, max_length=128)
    full_name: Optional[str] = Field(None, min_length=1, max_length=35)

    model_config = ConfigDict(exclude_unset=True)
