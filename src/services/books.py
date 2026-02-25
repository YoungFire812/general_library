import traceback
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from websockets import serve
from typing import List
from src.models.models import Book
from src.schemas.books import BookCreate, BookUpdate, BookRead
from src.schemas.categories import CategoryRead
from src.schemas.dto import ApiResponse
from src.utils.responses import ResponseHandler
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


class BookService:
    @staticmethod
    async def get_books_limited(
        db: AsyncSession, page: int, limit: int, search: str | None = None, category_id: int | None = None
    ) -> ApiResponse[List[BookRead]]:
        stmt = (
            select(Book)
            .options(selectinload(Book.category))
            .order_by(Book.id)
            .limit(limit)
            .offset((page - 1) * limit)
        )

        if search is not None:
            stmt = stmt.where(Book.title.ilike(f"%{search}%"))

        if category_id is not None:
            stmt = stmt.where(Book.category_id == category_id)

        result = await db.execute(stmt)
        books = result.scalars().all()

        data = [
            BookRead.model_validate(book)
            for book in books
        ]

        return ApiResponse(
            message=f"Page {page} with {limit} books",
            data=data
        )

    @staticmethod
    async def get_book(db: AsyncSession, book_id: int) -> ApiResponse[BookRead]:
        result = await db.execute(select(Book).options(selectinload(Book.category)).where(Book.id == book_id))
        book = result.scalar_one_or_none()

        if book is None:
            raise HTTPException(
                status_code=404, detail=f"Book with id {book_id} not found!"
            )

        return ApiResponse(
            message=f"Data for book with id {book_id}",
            data=BookRead.model_validate(book)
        )

    @staticmethod
    async def create_book(db: AsyncSession, book: BookCreate) -> ApiResponse[BookRead]:
        book_dict = book.model_dump(mode="json")
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

        return ApiResponse(
            message="Book created!",
            data=BookRead.model_validate(db_book_full)
        )
