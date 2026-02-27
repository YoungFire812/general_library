from sqlalchemy.ext.asyncio import AsyncSession
from src.models.models import Category
from src.schemas.categories import CategoryCreate
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from src.core.sqlErrors import UNIQUE_VIOLATION, is_error
from fastapi import HTTPException
from src.schemas.dto import ApiResponse
from src.schemas.categories import CategoryRead
from typing import List


class CategoryService:
    @staticmethod
    async def get_all_categories(db: AsyncSession) -> ApiResponse[List[CategoryRead]]:
        result = await db.execute(select(Category).order_by(Category.id.asc()))
        categories = result.scalars().all()
        return ApiResponse(
            message="All categories!",
            data=[CategoryRead.model_validate(category) for category in categories]
        )


    @staticmethod
    async def get_one_category(db: AsyncSession, category_id: int) -> ApiResponse[CategoryRead]:
        result = await db.execute(select(Category).where(Category.id == category_id))
        category = result.scalar_one_or_none()

        if category is None:
            raise HTTPException(404, f"Category with Id {category_id} Not Found!")

        return ApiResponse(
            message="Your category!",
            data=CategoryRead.model_validate(category)
        )

    @staticmethod
    async def create_category(db: AsyncSession, category: CategoryCreate) -> ApiResponse[CategoryRead]:
        category_dict = category.model_dump()
        db_category = Category(**category_dict)
        db.add(db_category)

        try:
            await db.commit()
            await db.refresh(db_category)
            return ApiResponse(
                message="The category has been created",
                data=CategoryRead.model_validate(db_category)
            )
        except IntegrityError as e:
            await db.rollback()
            if is_error(e, UNIQUE_VIOLATION):
                raise HTTPException(409, f"Category {category.name} is already exists!")
            else:
                raise
