from sqlalchemy.ext.asyncio import AsyncSession
from src.models.models import Category
from src.schemas.categories import CategoryCreate
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from src.core.sqlErrors import UNIQUE_VIOLATION, is_error
from fastapi import HTTPException
from src.schemas.dto import ApiResponse
from src.schemas.categories import CategoryRead, CategoryUpdate
from typing import List
from datetime import datetime, timezone


class CategoryService:
    @staticmethod
    async def get_all_categories(db: AsyncSession) -> ApiResponse[List[CategoryRead]]:
        result = await db.execute(select(Category).where(Category.deleted_at.is_(None)).order_by(Category.id.asc()))
        categories = result.scalars().all()
        return ApiResponse(
            message="All categories!",
            data=[CategoryRead.model_validate(category) for category in categories]
        )

    @staticmethod
    async def get_all_categories_including_deleted(db: AsyncSession) -> ApiResponse[List[CategoryRead]]:
        result = await db.execute(select(Category).order_by(Category.id.asc()))
        categories = result.scalars().all()
        return ApiResponse(
            message="All categories!",
            data=[CategoryRead.model_validate(category) for category in categories]
        )

    @staticmethod
    async def get_one_category(db: AsyncSession, category_id: int) -> ApiResponse[CategoryRead]:
        result = await db.execute(select(Category).where(Category.id == category_id, Category.deleted_at.is_(None)))
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

    @staticmethod
    async def update_category(db: AsyncSession, category_id: int, data: CategoryUpdate):
        result = await db.execute(
            select(Category).where(
                (Category.id == category_id) & (Category.deleted_at.is_(None))
            )
        )

        db_category = result.scalar_one_or_none()
        if db_category is None:
            raise HTTPException(status_code=404, detail="Category not found!")

        data = data.model_dump()
        if not data:
            raise HTTPException(400, "No fields to update")

        for field, value in data.items():
            if value is not None:
                setattr(db_category, field, value)

        try:
            await db.commit()
            await db.refresh(db_category)
            return CategoryRead.model_validate(db_category)

        except IntegrityError as e:
            await db.rollback()
            if is_error(e, UNIQUE_VIOLATION):
                raise HTTPException(409, f"Category with this name is already exists!")
            else:
                raise


    @staticmethod
    async def delete_category(db: AsyncSession, category_id: int):
        result = await db.execute(
            select(Category).where(
                (Category.id == category_id) & (Category.deleted_at.is_(None))
            )
        )

        db_category = result.scalar_one_or_none()
        if db_category is None:
            raise HTTPException(status_code=404, detail="Category not found!")

        db_category.deleted_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(db_category)

