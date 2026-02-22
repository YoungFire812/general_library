from fastapi import APIRouter, Body, Depends

from src.schemas.categories import CategoryCreate
from src.services.categories import CategoryService
from src.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession


categories_router = APIRouter(prefix="/categories")


@categories_router.post("", tags=["Categories"])
async def create_category(
    category: CategoryCreate = Body(...), db: AsyncSession = Depends(get_db)
):
    return await CategoryService.create_category(db, category)


@categories_router.get("", tags=["Categories"])
async def get_all_categories(db: AsyncSession = Depends(get_db)):
    return await CategoryService.get_all_categories(db)
