from fastapi import APIRouter, Depends
from src.schemas.categories import CategoryCreate
from src.services.categories import CategoryService
from src.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.dto import ApiResponse
from src.schemas.categories import CategoryRead
from typing import List


categories_router = APIRouter(prefix="/categories")


@categories_router.post("/create", tags=["Categories"], response_model=ApiResponse[CategoryRead])
async def create_category(category: CategoryCreate, db: AsyncSession = Depends(get_db)) -> ApiResponse[CategoryRead]:
    return await CategoryService.create_category(db, category)


@categories_router.get("/all", tags=["Categories"], response_model=ApiResponse[List[CategoryRead]])
async def get_all_categories(db: AsyncSession = Depends(get_db)) -> ApiResponse[List[CategoryRead]]:
    return await CategoryService.get_all_categories(db)

@categories_router.get("/{category_id}", tags=["Categories"], response_model=ApiResponse[CategoryRead])
async def get_one_category(category_id: int, db: AsyncSession = Depends(get_db)) -> ApiResponse[CategoryRead]:
    return await CategoryService.get_one_category(db, category_id)