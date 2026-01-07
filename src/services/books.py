import traceback

from sqlalchemy.ext.asyncio import AsyncSession
from src.models.models import Book, Category
from src.schemas.books import BookCreate, BookUpdate
from src.utils.responses import ResponseHandler
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload



class BookService:
    @staticmethod
    async def get_books_limited(db: AsyncSession, page: int, limit: int, search: str = ""):
        result = await db.execute(
            select(Book)
            .options(selectinload(Book.category))
            .order_by(Book.id.asc())
            .filter(Book.title.contains(search))
            .limit(limit)
            .offset((page - 1) * limit)
        )

        books = result.scalars().all()
        data = [
            {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "description": book.description,
                "stock": book.stock,
                "thumbnail": book.thumbnail,
                "images": book.images,
                "is_published": book.is_published,
                "created_at": book.created_at,
                "category": book.category.name,
            }
            for book in books
        ]

        return {
            "message": f"Page {page} with {limit} books",
            "data": data
        }

    @staticmethod
    async def get_book(db: AsyncSession, book_id: int):
        result = await db.execute(select(Book).filter(Book.id == book_id))
        book = result.scalars().first()

        if not book:
            await ResponseHandler.not_found_error("Book", book_id)

        return await ResponseHandler.get_single_success(book.title, book_id, book)

    @staticmethod
    async def create_book(db: AsyncSession, book: BookCreate):
        try:
            book_dict = book.model_dump()
            book_dict['thumbnail'] = str(book_dict['thumbnail'])
            book_dict['images'] = [str(url) for url in book_dict['images']]
            db_book = Book(**book_dict)
            db.add(db_book)
            await db.commit()
            await db.refresh(db_book)
        except:
            print(traceback.format_exc())
        return await ResponseHandler.create_success(db_book.title, db_book.id, db_book)

    @staticmethod
    async def update_book(db: AsyncSession, book_id: int, updated_book: BookUpdate):
        result = await db.execute(select(Book).filter(Book.id == book_id))
        db_book = result.scalars().first()
        if not db_book:
            await ResponseHandler.not_found_error("Book", book_id)

        for key, value in updated_book.model_dump().items():
            setattr(db_book, key, value)

        await db.commit()
        await db.refresh(db_book)
        return await ResponseHandler.update_success(db_book.title, db_book.id, db_book)

    @staticmethod
    async def delete_book(db: AsyncSession, book_id: int):
        result = await db.execute(select(Book).filter(Book.id == book_id))
        db_book = result.scalars().first()
        if not db_book:
            await ResponseHandler.not_found_error("Book", book_id)

        await db.delete(db_book)
        await db.commit()
        return await ResponseHandler.delete_success(db_book.title, db_book.id, db_book)