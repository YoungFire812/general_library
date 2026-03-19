from fastapi import APIRouter, Depends
from src.schemas.categories import CategoryCreate, CategoryUpdate
from src.services.categories import CategoryService
from src.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.categories import CategoryRead
from typing import List
from src.core.deps import dev_verify_admin
from src.schemas.users import UserRead


categories_router = APIRouter(prefix="/categories")


@categories_router.get("/all", tags=["Categories"], response_model=List[CategoryRead])
async def get_all_categories(db: AsyncSession = Depends(get_db)) -> List[CategoryRead]:
    return await CategoryService.get_all_categories(db)


@categories_router.get(
    "/{category_id}", tags=["Categories"], response_model=CategoryRead
)
async def get_one_category(
    category_id: int, db: AsyncSession = Depends(get_db)
) -> CategoryRead:
    return await CategoryService.get_one_category(db, category_id)


@categories_router.post("/create", tags=["Categories"], response_model=CategoryRead)
async def create_category(
    category: CategoryCreate, db: AsyncSession = Depends(get_db)
) -> CategoryRead:
    return await CategoryService.create_category(db, category)


@categories_router.patch("/patch", tags=["Categories"], response_model=CategoryRead)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: UserRead = Depends(dev_verify_admin),
) -> CategoryRead:
    return await CategoryService.update_category(db, category_id, data)


@categories_router.delete("/{category_id}", tags=["Categories"], status_code=204)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: UserRead = Depends(dev_verify_admin),
):
    await CategoryService.delete_category(db, category_id)
