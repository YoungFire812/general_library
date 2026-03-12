from pydantic import BaseModel, ConfigDict, HttpUrl, Field
from datetime import datetime
from typing import List, Optional
from src.schemas.categories import CategoryRead


class BookBase(BaseModel):
    title: str = Field(min_length=1, max_length=25)
    author: str = Field(min_length=1, max_length=25)
    description: str = Field(min_length=1, max_length=350)
    stock: bool = True
    thumbnail: HttpUrl
    images: List[HttpUrl]
    is_published: bool = True
    category_id: int = Field(ge=1)
    owner_id: int


class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str]
    author: Optional[str]
    description: Optional[str]
    stock: Optional[bool]
    thumbnail: Optional[HttpUrl]
    images: Optional[List[HttpUrl]]
    is_published: Optional[bool]
    category_id: Optional[int] = Field(ge=1)

    model_config = ConfigDict(exclude_unset=True)

class BookRead(BaseModel):
    id: int
    title: str = Field(min_length=1, max_length=25)
    author: str = Field(min_length=1, max_length=25)
    description: str = Field(min_length=1, max_length=350)
    stock: bool = True
    thumbnail: HttpUrl
    images: List[HttpUrl]
    is_published: bool = True
    created_at: datetime
    deleted_at: datetime | None = None
    category: CategoryRead
    owner_id: int

    model_config = ConfigDict(from_attributes=True)
