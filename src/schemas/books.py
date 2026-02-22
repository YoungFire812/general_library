from pydantic import BaseModel, ConfigDict, HttpUrl
from datetime import datetime
from typing import List


class BookBase(BaseModel):
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
class BookCreate(BookBase):
    pass


# Update Book
class BookUpdate(BookBase):
    pass


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
