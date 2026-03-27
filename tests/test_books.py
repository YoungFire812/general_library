import pytest
from src.services.books import BookService
from src.schemas.books import *
from fastapi import HTTPException
from src.models.models import Book, User


class TestCreateBook:
    @pytest.mark.asyncio
    async def test_create_book_success(self, db_session, test_user_first, test_category):
        book_data = BookCreate(
            title="Test Book",
            author="Author",
            description="Desc",
            owner_id=test_user_first.id,
            category_id=test_category.id,
            thumbnail="http://test.com/thumb.jpg",
            images=["http://test.com/1.jpg", "http://test.com/2.jpg"],
        )

        result = await BookService.create_book(db_session, book_data, test_user_first)

        assert result.id is not None
        assert result.title == "Test Book"
        assert result.category.id == test_category.id
        assert result.owner_id == test_user_first.id

    @pytest.mark.asyncio
    async def test_create_book_permission_denied(self, db_session, test_user_first, test_category):
        book_data = BookCreate(
            title="Test Book",
            author="Author",
            description="Desc",
            owner_id=999,
            category_id=test_category.id,
            thumbnail="http://test.com/thumb.jpg",
            images=["http://test.com/1.jpg"],
        )

        with pytest.raises(HTTPException) as exc:
            await BookService.create_book(db_session, book_data, test_user_first)

        assert exc.value.status_code == 403

    @pytest.mark.asyncio
    async def test_create_book_category_not_found(self, db_session, test_user_first):
        book_data = BookCreate(
            title="Test Book",
            author="Author",
            description="Desc",
            owner_id=test_user_first.id,
            category_id=999,
            thumbnail="http://test.com/thumb.jpg",
            images=["http://test.com/1.jpg"],
        )

        with pytest.raises(HTTPException) as exc:
            await BookService.create_book(db_session, book_data, test_user_first)

        assert exc.value.status_code == 404

class TestUpdateBook:
    @pytest.mark.asyncio
    async def test_update_book_success(self, db_session, test_user_first, test_category):
        book = Book(
            title="Old",
            author="Author",
            description="Desc",
            owner_id=test_user_first.id,
            category_id=test_category.id,
            thumbnail="https://old.jpg",
            images=[]
        )
        db_session.add(book)
        await db_session.flush()

        data = BookUpdate(title="New Title")

        result = await BookService.update_book(db_session, test_user_first, book.id, data)

        assert result.title == "New Title"
        assert result.author == "Author"
        assert result.description == "Desc"
        assert result.thumbnail == "https://old.jpg"
        assert result.images == []

    @pytest.mark.asyncio
    async def test_update_book_not_found(self, db_session, test_user_first):
        data = BookUpdate(title="New")

        with pytest.raises(HTTPException) as exc:
            await BookService.update_book(db_session, test_user_first, 999, data)

        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_update_book_not_owner(self, db_session, test_user_first, test_user_second, test_category):
        book = Book(
            title="Old",
            author="Author",
            description="Desc",
            owner_id=test_user_second.id,
            category_id=test_category.id,
            thumbnail="old",
            images=[],
            status="available"
        )
        db_session.add(book)
        await db_session.flush()

        data = BookUpdate(title="New")

        with pytest.raises(HTTPException) as exc:
            await BookService.update_book(db_session, test_user_first, book.id, data)

        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_update_book_invalid_status(self, db_session, test_user_first, test_category):
        book = Book(
            title="Old",
            author="Author",
            description="Desc",
            owner_id=test_user_first.id,
            category_id=test_category.id,
            thumbnail="old",
            images=[],
            status="reserved"
        )
        db_session.add(book)
        await db_session.flush()

        data = BookUpdate(title="New")

        with pytest.raises(HTTPException) as exc:
            await BookService.update_book(db_session, test_user_first, book.id, data)

        assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_update_book_empty_data(self, db_session, test_user_first, test_category):
        book = Book(
            title="Old",
            author="Author",
            description="Desc",
            owner_id=test_user_first.id,
            category_id=test_category.id,
            thumbnail="https://old.jpg",
            images=[],
            status="available"
        )
        db_session.add(book)
        await db_session.flush()

        data = BookUpdate()

        with pytest.raises(HTTPException) as exc:
            await BookService.update_book(db_session, test_user_first, book.id, data)

        assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_update_book_category_not_found(self, db_session, test_user_first, test_category):
        book = Book(
            title="Old",
            author="Author",
            description="Desc",
            owner_id=test_user_first.id,
            category_id=test_category.id,
            thumbnail="old",
            images=[],
            status="available"
        )
        db_session.add(book)
        await db_session.flush()

        data = BookUpdate(category_id=999)

        with pytest.raises(HTTPException) as exc:
            await BookService.update_book(db_session, test_user_first, book.id, data)

        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_update_book_deleted_book_not_found(self, db_session, test_user_first, test_category):
        from datetime import datetime, timezone

        book = Book(
            title="Old",
            author="Author",
            description="Desc",
            owner_id=test_user_first.id,
            category_id=test_category.id,
            thumbnail="old",
            images=[],
            status="available",
            deleted_at=datetime.now(timezone.utc)
        )
        db_session.add(book)
        await db_session.flush()

        data = BookUpdate(title="New")

        with pytest.raises(HTTPException) as exc:
            await BookService.update_book(db_session, test_user_first, book.id, data)

        assert exc.value.status_code == 404

class TestDeleteBook:
    @pytest.mark.asyncio
    async def test_delete_book_success(self, db_session, test_user_first, test_category):
        book = Book(
            title="Test",
            author="Author",
            description="Desc",
            owner_id=test_user_first.id,
            category_id=test_category.id,
            thumbnail="https://test.jpg",
            images=[],
            status="available"
        )
        db_session.add(book)
        await db_session.flush()

        await BookService.delete_book(db_session, book.id, test_user_first)

        assert book.deleted_at is not None
        assert book.status == "deleted"

    @pytest.mark.asyncio
    async def test_delete_book_not_found(self, db_session, test_user_first):
        with pytest.raises(HTTPException) as exc:
            await BookService.delete_book(db_session, 999, test_user_first)

        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_book_not_owner(self, db_session, test_user_first, test_user_second, test_category):
        book = Book(
            title="Test",
            author="Author",
            description="Desc",
            owner_id=test_user_second.id,
            category_id=test_category.id,
            thumbnail="https://test.jpg",
            images=[],
            status="available"
        )
        db_session.add(book)
        await db_session.flush()

        with pytest.raises(HTTPException) as exc:
            await BookService.delete_book(db_session, book.id, test_user_first)

        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_book_already_deleted(self, db_session, test_user_first, test_category):
        from datetime import datetime, timezone
        book = Book(
            title="Test",
            author="Author",
            description="Desc",
            owner_id=test_user_first.id,
            category_id=test_category.id,
            thumbnail="https://test.jpg",
            images=[],
            status="deleted",
            deleted_at=datetime.now(timezone.utc)
        )
        db_session.add(book)
        await db_session.flush()

        with pytest.raises(HTTPException) as exc:
            await BookService.delete_book(db_session, book.id, test_user_first)

        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_book_invalid_status(self, db_session, test_user_first, test_category):
        book = Book(
            title="Test",
            author="Author",
            description="Desc",
            owner_id=test_user_first.id,
            category_id=test_category.id,
            thumbnail="https://test.jpg",
            images=[],
            status="reserved"
        )
        db_session.add(book)
        await db_session.flush()

        with pytest.raises(HTTPException) as exc:
            await BookService.delete_book(db_session, book.id, test_user_first)

        assert exc.value.status_code == 400

class TestGetBook:
    @pytest.mark.asyncio
    async def test_get_book_success(self, db_session, test_user_first, test_category):
        book = Book(
            title="Test",
            author="Author",
            description="Desc",
            owner_id=test_user_first.id,
            category_id=test_category.id,
            thumbnail="https://test.jpg",
            images=[],
            status="available"
        )
        db_session.add(book)
        await db_session.flush()

        result = await BookService.get_book(db_session, book.id)

        assert result.id == book.id
        assert result.title == "Test"
        assert result.category.id == test_category.id

    @pytest.mark.asyncio
    async def test_get_book_not_found(self, db_session):
        with pytest.raises(HTTPException) as exc:
            await BookService.get_book(db_session, 999)

        assert exc.value.status_code == 404
        assert "not found" in exc.value.detail.lower()

    @pytest.mark.asyncio
    async def test_get_book_deleted(self, db_session, test_user_first, test_category):
        from datetime import datetime, timezone
        book = Book(
            title="Test",
            author="Author",
            description="Desc",
            owner_id=test_user_first.id,
            category_id=test_category.id,
            thumbnail="https://test.jpg",
            images=[],
            status="available",
            deleted_at=datetime.now(timezone.utc)
        )
        db_session.add(book)
        await db_session.flush()

        with pytest.raises(HTTPException) as exc:
            await BookService.get_book(db_session, book.id)

        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_book_with_category_loaded(self, db_session, test_user_first, test_category):
        book = Book(
            title="Test",
            author="Author",
            description="Desc",
            owner_id=test_user_first.id,
            category_id=test_category.id,
            thumbnail="https://test.jpg",
            images=[],
            status="available"
        )
        db_session.add(book)
        await db_session.flush()

        result = await BookService.get_book(db_session, book.id)

        assert result.category.id == test_category.id

class TestGetBooksLimited:
    @pytest.mark.asyncio
    async def test_get_books_limited_basic(self, db_session, test_user_first, test_category):
        books = [
            Book(
                title=f"Book {i}",
                author="Author",
                description="Desc",
                owner_id=test_user_first.id,
                category_id=test_category.id,
                thumbnail="https://test.jpg",
                images=[],
                status="available",
                is_published=True
            )
            for i in range(5)
        ]
        db_session.add_all(books)
        await db_session.flush()

        result = await BookService.get_books_limited(db_session, limit=2, offset=1)

        assert len(result) == 2
        assert result[0].title == "Book 1"

    @pytest.mark.asyncio
    async def test_get_books_limited_search(self, db_session, test_user_first, test_category):
        book1 = Book(
            title="Python Book",
            author="A",
            description="D",
            owner_id=test_user_first.id,
            category_id=test_category.id,
            thumbnail="https://test.jpg",
            images=[],
            status="available",
            is_published=True
        )
        book2 = Book(
            title="Java Book",
            author="A",
            description="D",
            owner_id=test_user_first.id,
            category_id=test_category.id,
            thumbnail="https://test.jpg",
            images=[],
            status="available",
            is_published=True
        )

        db_session.add_all([book1, book2])
        await db_session.flush()

        result = await BookService.get_books_limited(db_session, 10, 0, search="Python")

        assert len(result) == 1
        assert result[0].title == "Python Book"

    @pytest.mark.asyncio
    async def test_get_books_limited_category_filter(self, db_session, test_user_first, test_category, another_category):
        book1 = Book(
            title="Book 1",
            author="A",
            description="D",
            owner_id=test_user_first.id,
            category_id=test_category.id,
            thumbnail="https://test.jpg",
            images=[],
            status="available",
            is_published=True
        )
        book2 = Book(
            title="Book 2",
            author="A",
            description="",
            owner_id=test_user_first.id,
            category_id=another_category.id,
            thumbnail="https://test.jpg",
            images=[],
            status="available",
            is_published=True
        )

        db_session.add_all([book1, book2])
        await db_session.flush()

        result = await BookService.get_books_limited(db_session, 10, 0, category_id=test_category.id)

        assert len(result) == 1
        assert result[0].category.id == test_category.id

    @pytest.mark.asyncio
    async def test_get_books_limited_excludes_deleted(self, db_session, test_user_first, test_category):
        from datetime import datetime, timezone
        book = Book(
            title="Deleted Book",
            author="A",
            description="D",
            owner_id=test_user_first.id,
            category_id=test_category.id,
            thumbnail="https://test.jpg",
            images=[],
            status="available",
            is_published=True,
            deleted_at=datetime.now(timezone.utc)
        )
        db_session.add(book)
        await db_session.flush()
    
        result = await BookService.get_books_limited(db_session, 10, 0)
    
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_books_limited_excludes_unpublished(self, db_session, test_user_first, test_category):
        book = Book(
            title="Hidden Book",
            author="A",
            description="D",
            owner_id=test_user_first.id,
            category_id=test_category.id,
            thumbnail="https://test.jpg",
            images=[],
            status="available",
            is_published=False
        )
        db_session.add(book)
        await db_session.flush()

        result = await BookService.get_books_limited(db_session, 10, 0)

        assert len(result) == 0