from pydantic import BaseModel, ConfigDict, HttpUrl, Field
from datetime import datetime
from typing import List
from src.schemas.categories import CategoryBase



class BookBase(BaseModel):
    id: int
    title: str
    author: str
    description: str
    stock: bool
    thumbnail: HttpUrl
    images: List[HttpUrl]
    is_published: bool
    created_at: datetime
    category_id: int

    model_config = ConfigDict(from_attributes=True, json_encoders={HttpUrl: str})


# Create Book
class BookCreate(BaseModel):
    title: str
    author: str
    description: str
    stock: bool
    thumbnail: HttpUrl
    images: List[HttpUrl]
    is_published: bool
    created_at: datetime
    category_id: int

    model_config = ConfigDict(from_attributes=True, json_encoders={HttpUrl: str})


# Update Book
class BookUpdate(BaseModel):
    title: str
    author: str
    description: str
    stock: bool
    thumbnail: HttpUrl
    images: List[HttpUrl]
    is_published: bool
    created_at: datetime
    category_id: int

    model_config = ConfigDict(from_attributes=True, json_encoders={HttpUrl: str})


# Get Book
class BookOut(BaseModel):
    message: str
    data: BookBase

    model_config = ConfigDict(from_attributes=True, json_encoders={HttpUrl: str})


class BooksOut(BaseModel):
    message: str
    data: List[BookBase]

    model_config = ConfigDict(from_attributes=True, json_encoders={HttpUrl: str})


# Delete Book
class BookDelete(BookBase):
    pass


class BookOutDelete(BaseModel):
    message: str
    data: BookDelete

    model_config = ConfigDict(from_attributes=True, json_encoders={HttpUrl: str})
