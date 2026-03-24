from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from src.models.models import Book, Category
from src.schemas.books import BookCreate, BookUpdate, BookRead
from src.schemas.users import UserRead
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
from logutu import logger


class BookService:
    @staticmethod
    async def get_books_limited(
        db: AsyncSession,
        limit: int,
        offset: int,
        search: str | None = None,
        category_id: int | None = None,
    ) -> List[BookRead]:
        stmt = (
            select(Book)
            .options(selectinload(Book.category))
            .where(Book.deleted_at.is_(None), Book.is_published.is_(True))
            .order_by(Book.id)
            .limit(limit)
            .offset(offset)
        )

        if search is not None:
            stmt = stmt.where(Book.title.ilike(f"%{search}%"))

        if category_id is not None:
            stmt = stmt.where(Book.category_id == category_id)

        result = await db.execute(stmt)
        books = result.scalars().all()

        data = [BookRead.model_validate(book) for book in books]

        logger.info("Books fetched with limit", count=len(books), limit=limit, offset=offset)
        return data

    @staticmethod
    async def get_book(db: AsyncSession, book_id: int) -> BookRead:
        result = await db.execute(
            select(Book)
            .options(selectinload(Book.category))
            .where(Book.id == book_id, Book.deleted_at.is_(None))
        )
        book = result.scalar_one_or_none()

        if book is None:
            logger.warning("Book not found", book_id=book_id)
            raise HTTPException(
                status_code=404, detail=f"Book with id {book_id} not found!"
            )

        logger.info("Book fetched successfully", book_id=book_id)
        return BookRead.model_validate(book)

    @staticmethod
    async def create_book(db: AsyncSession, book: BookCreate, user: UserRead) -> BookRead:
        if book.owner_id != user.id:
            logger.warning("Permission denied on create book")
            raise HTTPException(403, "permission denied")

        book_dict = book.model_dump()

        book_dict["thumbnail"] = str(book_dict["thumbnail"])
        book_dict["images"] = [str(url) for url in book_dict["images"]]

        result = await db.execute(
            select(Category).where(Category.id == book_dict["category_id"])
        )

        if result.scalar_one_or_none() is None:
            logger.warning("Category not found for new book", category_id=book_dict["category_id"])
            raise HTTPException(404, "Category not found")

        db_book = Book(**book_dict)
        db.add(db_book)
        await db.commit()
        await db.refresh(db_book)

        result = await db.execute(
            select(Book)
            .options(selectinload(Book.category))
            .where(Book.id == db_book.id)
        )
        db_book_full = result.scalar_one()

        logger.info("Book created successfully", book_id=db_book_full.id, category_id=db_book_full.category_id)
        return BookRead.model_validate(db_book_full)

    @staticmethod
    async def update_book(
        db: AsyncSession, user: UserRead, book_id: int, data: BookUpdate
    ):
        async with db.begin():
            result = await db.execute(
                select(Book)
                .where(Book.id == book_id, Book.deleted_at.is_(None), Book.owner_id == user.id)
                .options(selectinload(Book.category))
                .with_for_update()
            )
            db_book = result.scalar_one_or_none()

            if db_book is None:
                logger.warning("Book not found for update", book_id=book_id)
                raise HTTPException(status_code=404, detail="Book not found!")
            elif db_book.status != "available":
                logger.warning("Book cannot be modified, currently in order", book_id=book_id)
                raise HTTPException(400, "Cannot modify, book in order")

            data = data.model_dump()
            if not data:
                logger.warning("No fields to update for book", book_id=book_id)
                raise HTTPException(400, "No fields to update")

            if data.get("thumbnail") is not None:
                data["thumbnail"] = str(data["thumbnail"])

            if data.get("images") is not None:
                data["images"] = [str(url) for url in data["images"]]

            if data.get("category_id") is not None:
                result = await db.execute(
                    select(Category).where(Category.id == data["category_id"])
                )

                if result.scalar_one_or_none() is None:
                    logger.warning("Category not found for book update", category_id=data["category_id"])
                    raise HTTPException(404, "Category not found")

            for field, value in data.items():
                if value is not None:
                    setattr(db_book, field, value)

        logger.info("Book updated successfully", book_id=book_id, updated_fields=list(data.keys()))
        return BookRead.model_validate(db_book)

    @staticmethod
    async def delete_book(db: AsyncSession, book_id: int, user: UserRead):
        async with db.begin():
            result = await db.execute(
                select(Book)
                .where(Book.id == book_id, Book.deleted_at.is_(None), Book.owner_id == user.id)
                .with_for_update()
            )
            db_book = result.scalar_one_or_none()

            if db_book is None:
                logger.warning("Book not found for delete", book_id=book_id)
                raise HTTPException(status_code=404, detail="Book not found!")
            elif db_book.status != "available":
                logger.warning("Book cannot be deleted, currently in order", book_id=book_id)
                raise HTTPException(400, "Cannot modify, book in order")

            db_book.deleted_at = datetime.now(timezone.utc)
            db_book.status = "deleted"

        logger.info("Book soft-deleted successfully", book_id=book_id)
