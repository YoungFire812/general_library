from fastapi import APIRouter, Body, Depends, Query
from watchfiles import awatch

from src.schemas.books import BookCreate
from src.services.books import BookService
from src.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession


books_router = APIRouter(prefix="/books")

@books_router.post("")
async def create_book(book: BookCreate = Body(...), db: AsyncSession = Depends(get_db)):
    return await BookService.create_book(db, book)

@books_router.get("")
async def get_books_limited(
        db: AsyncSession = Depends(get_db),
        page: int = Query(1, ge=1),
        limit: int = Query(24, ge=1, le=100)
):
    return await BookService.get_books_limited(db, page, limit)