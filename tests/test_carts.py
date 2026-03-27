import pytest
from fastapi import HTTPException
from datetime import datetime, timezone
from src.services.carts import CartService
from src.models.models import Cart, CartItem, Book
from src.schemas.carts import CartItemCreate, CartItemRead
from src.schemas.books import BookRead


@pytest.mark.asyncio
class TestAddProductToCart:
    async def test_add_product_success(self, db_session, test_user_first, test_category):
        cart = Cart(user_id=test_user_first.id)
        db_session.add(cart)
        await db_session.flush()

        book = Book(
            title="Test Book",
            author="Author",
            description="Desc",
            thumbnail="img.png",
            category_id=test_category.id,
            owner_id=test_user_first.id,
            is_published=True
        )
        db_session.add(book)
        await db_session.flush()

        product_data = CartItemCreate(cart_id=cart.id, book_id=book.id)
        result = await CartService.add_product_to_cart(db_session, test_user_first.id, product_data)

        assert isinstance(result, CartItemRead)
        assert result.cart_id == cart.id
        assert result.book_id == book.id

    async def test_add_product_unauthorized(self, db_session, test_user_first, test_user_second, test_category):
        cart = Cart(user_id=test_user_second.id)
        db_session.add(cart)
        await db_session.flush()

        book = Book(
            title="Test Book2",
            author="Author",
            description="Desc",
            thumbnail="img2.png",
            category_id=test_category.id,
            owner_id=test_user_first.id,
            is_published=True
        )
        db_session.add(book)
        await db_session.flush()

        product_data = CartItemCreate(cart_id=cart.id, book_id=book.id)
        with pytest.raises(HTTPException) as exc:
            await CartService.add_product_to_cart(db_session, test_user_first.id, product_data)
        assert exc.value.status_code == 403

@pytest.mark.asyncio
class TestGetLimitedUserProduct:
    async def test_no_products_returns_empty_list(self, db_session, test_user_first):
        cart = Cart(user_id=test_user_first.id)
        db_session.add(cart)
        await db_session.flush()

        result = await CartService.get_limited_user_product(db_session, test_user_first.id, limit=10, offset=0)
        assert result == []

    async def test_products_fetched_successfully(self, db_session, test_user_first, test_category):
        cart = Cart(user_id=test_user_first.id)
        db_session.add(cart)
        await db_session.flush()

        books = []
        for i in range(5):
            book = Book(
                title=f"Book {i}",
                author="Author",
                description="Desc",
                thumbnail=f"img{i}.png",
                category_id=test_category.id,
                owner_id=test_user_first.id,
                is_published=True
            )
            db_session.add(book)
            await db_session.flush()

            cart_item = CartItem(cart_id=cart.id, book_id=book.id)
            db_session.add(cart_item)
            await db_session.flush()
            books.append(book)

        result = await CartService.get_limited_user_product(db_session, test_user_first.id, limit=3, offset=1)
        assert len(result) == 3
        assert all(isinstance(b, BookRead) for b in result)

@pytest.mark.asyncio
class TestGetUserCart:
    async def test_cart_fetched_successfully(self, db_session, test_user_first):
        cart = Cart(user_id=test_user_first.id)
        db_session.add(cart)
        await db_session.flush()

        result = await CartService.get_user_cart(db_session, test_user_first.id)
        assert result.id == cart.id
        assert result.user_id == test_user_first.id


