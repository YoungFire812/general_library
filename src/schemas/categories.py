from typing import List
from pydantic import BaseModel, ConfigDict


class CategoryBase(BaseModel):
    id: int
    name: str

class CategoryRead(CategoryBase):
    pass

    model_config = ConfigDict(from_attributes=True)

class CategoryCreate(BaseModel):
    name: str


