from fastapi import APIRouter, Depends, Query
from pydantic import Field
from src.schemas.books import BookCreate, BookRead
from src.services.books import BookService
from src.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.dto import ApiResponse
from typing import List
from src.core.deps import Pagination

books_router = APIRouter(prefix="/books")


@books_router.post("", tags=["Books"], response_model=ApiResponse[BookRead], status_code=201)
async def create_book(book: BookCreate, db: AsyncSession = Depends(get_db)) -> ApiResponse[BookRead]:
    return await BookService.create_book(db, book)


@books_router.get("/get_limited", tags=["Books"], response_model=ApiResponse[List[BookRead]])
async def get_books_limited(
    db: AsyncSession = Depends(get_db),
    pagination: Pagination = Depends(),
    search: str | None = None,
    category_id: int | None = Query(default=None, ge=1)
) -> ApiResponse[List[BookRead]]:
    return await BookService.get_books_limited(db, pagination.page, pagination.limit, search, category_id)


@books_router.get("/{book_id}", tags=["Books"], response_model=ApiResponse[BookRead])
async def get_one_book(book_id: int, db: AsyncSession = Depends(get_db)) -> ApiResponse[BookRead]:
    return await BookService.get_book(db, book_id)