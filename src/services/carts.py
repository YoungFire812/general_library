from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.models import Cart, CartItem, Book
from src.schemas.books import BookRead
from src.schemas.carts import CartItemCreate, CartRead, CartItemRead
from src.utils.responses import ResponseHandler
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from src.schemas.dto import ApiResponse
from typing import List
from src.core.sqlErrors import is_error, UNIQUE_VIOLATION
from sqlalchemy.exc import IntegrityError


class CartService:
    @staticmethod
    async def add_product_to_cart(db: AsyncSession, user_id: int, product: CartItemCreate) -> ApiResponse[CartItemRead]:
        cart = await db.get(Cart, product.cart_id)
        if not cart or cart.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not allowed to modify this cart")

        db_cart_item = CartItem(**product.model_dump())
        db.add(db_cart_item)
        try:
            await db.commit()
            await db.refresh(db_cart_item)
            return ApiResponse(
                message="Item added to cart!",
                data=CartItemRead.model_validate(db_cart_item)
            )
        except IntegrityError as e:
            await db.rollback()
            if is_error(e, UNIQUE_VIOLATION):
                raise HTTPException(
                    status_code=409, detail="This book is already in the cart"
                )
            else:
                raise

    @staticmethod
    async def get_limited_user_product(
        db: AsyncSession, user_id: int, limit: int, offset: int
    ) -> ApiResponse[List[BookRead]]:
        result_user_id = await db.execute(select(Cart.id).where(Cart.user_id == user_id))
        cart_id = result_user_id.scalar_one()

        result_book_ids = await db.execute(select(CartItem.book_id).where(CartItem.cart_id == cart_id))
        book_ids = result_book_ids.scalars().all()

        if not book_ids:
            return ApiResponse(
                message="Books not found",
                data=[]
            )

        result_books = await db.execute(
            select(Book)
            .options(selectinload(Book.category))
            .where(Book.id.in_(book_ids))
            .offset(offset)
            .limit(limit)
        )

        books = result_books.scalars().all()

        return ApiResponse(
            message="All book",
            data=[BookRead.model_validate(book) for book in books]
        )


    @staticmethod
    async def get_user_cart(db: AsyncSession, user_id: int) -> ApiResponse[CartRead]:
        result = await db.execute(select(Cart).where(Cart.user_id == user_id))
        cart_obj = result.scalar_one()

        return ApiResponse(
            message=f"Cart id from user {user_id}",
            data=CartRead.model_validate(cart_obj)
        )
