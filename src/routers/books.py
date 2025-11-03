from fastapi import APIRouter, Body, Depends

from src.schemas.books import BookCreate
from src.services.books import BookService
from src.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession


books_router = APIRouter(prefix="/books")

@books_router.post("")
async def create_book(book: BookCreate = Body(...), db: AsyncSession = Depends(get_db)):
    return await BookService.create_book(db, book)

