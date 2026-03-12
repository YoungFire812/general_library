from fastapi import APIRouter, Depends, Query
from pydantic import Field
from src.schemas.books import BookCreate, BookRead, BookUpdate
from src.services.books import BookService
from src.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.dto import ApiResponse
from typing import List
from src.core.deps import Pagination, dev_get_current_user
from src.schemas.users import UserRead


books_router = APIRouter(prefix="/books", tags=["Books"])


@books_router.get("/get_limited", response_model=ApiResponse[List[BookRead]])
async def get_books_limited(
    db: AsyncSession = Depends(get_db),
    pagination: Pagination = Depends(),
    search: str | None = None,
    category_id: int | None = Query(default=None, ge=1)
) -> ApiResponse[List[BookRead]]:
    return await BookService.get_books_limited(db, pagination.page, pagination.limit, search, category_id)


@books_router.get("/{book_id}", response_model=ApiResponse[BookRead])
async def get_one_book(book_id: int, db: AsyncSession = Depends(get_db)) -> ApiResponse[BookRead]:
    return await BookService.get_book(db, book_id)


@books_router.post("", response_model=ApiResponse[BookRead], status_code=201)
async def create_book(book: BookCreate, db: AsyncSession = Depends(get_db)) -> ApiResponse[BookRead]:
    return await BookService.create_book(db, book)


@books_router.patch("/{book_id}", response_model=BookRead)
async def update_book(book_id: int, data: BookUpdate, db: AsyncSession = Depends(get_db), user: UserRead = Depends(dev_get_current_user)) -> BookRead:
    return await BookService.update_book(db, user.id, book_id, data)


@books_router.delete("/{book_id}", status_code=204)
async def delete_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    user: UserRead = Depends(dev_get_current_user),
):
    await BookService.delete_book(db, book_id, user.id)