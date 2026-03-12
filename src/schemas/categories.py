from typing import List
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class CategoryBase(BaseModel):
    name: str

class CategoryRead(CategoryBase):
    id: int
    deleted_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    pass


