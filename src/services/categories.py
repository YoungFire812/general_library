
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.models import Category
from src.schemas.categories import CategoryCreate, CategoryUpdate
from src.utils.responses import ResponseHandler
from sqlalchemy.future import select


class CategoryService:
    @staticmethod
    async def get_all_categories(db: AsyncSession):
        result = await db.execute(select(Category).order_by(Category.id.asc()))

        categories = result.scalars().all()

        return await ResponseHandler.success("Success", categories)

    @staticmethod
    async def get_category(db: AsyncSession, category_id: int):
        result = await db.execute(select(Category).filter(Category.id == category_id))
        category = result.scalars().first()

        if not category:
            await ResponseHandler.not_found_error("Category", category_id)

        return await ResponseHandler.get_single_success(
            category.name, category_id, category
        )

    @staticmethod
    async def create_category(db: AsyncSession, category: CategoryCreate):
        category_dict = category.model_dump()
        db_category = Category(**category_dict)
        db.add(db_category)
        await db.commit()
        await db.refresh(db_category)
        return await ResponseHandler.create_success(
            db_category.name, db_category.id, db_category
        )

    @staticmethod
    async def update_category(
        db: AsyncSession, category_id: int, updated_book: CategoryUpdate
    ):
        result = await db.execute(select(Category).filter(Category.id == category_id))
        db_category = result.scalars().first()
        if not db_category:
            await ResponseHandler.not_found_error("Category", category_id)

        for key, value in updated_book.model_dump().items():
            setattr(db_category, key, value)

        await db.commit()
        await db.refresh(db_category)
        return await ResponseHandler.update_success(
            db_category.name, db_category.id, db_category
        )

    @staticmethod
    async def delete_category(db: AsyncSession, category_id: int):
        result = await db.execute(select(Category).filter(Category.id == category_id))
        db_category = result.scalars().first()
        if not db_category:
            await ResponseHandler.not_found_error("Category", category_id)

        await db.delete(db_category)
        await db.commit()
        return await ResponseHandler.delete_success(
            db_category.name, db_category.id, db_category
        )
