from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.models import Cart, CartItem
from src.schemas.carts import CartItemCreate, CartRead
from src.utils.responses import ResponseHandler
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from src.schemas.dto import ApiResponse


class CartService:
    @staticmethod
    async def add_product_to_cart(
        db: AsyncSession, user_id: int, product: CartItemCreate
    ):
        db_cart_item = CartItem(**product.model_dump())
        db.add(db_cart_item)
        await db.commit()
        await db.refresh(db_cart_item)
        return await ResponseHandler.create_success(
            "product add to cart", db_cart_item.id, db_cart_item
        )

    @staticmethod
    async def delete_product_from_cart(db: AsyncSession, cart_item: CartRead):
        result = await db.execute(
            select(CartItem).filter(
                CartItem.cart_id == cart_item.cart_id,
                CartItem.book_id == cart_item.book_id,
            )
        )
        db_cart_item = result.scalars().first()
        if not db_cart_item:
            await ResponseHandler.not_found_error(
                "CartItem", f"{cart_item.cart_id} and {cart_item.book_id}"
            )

        await db.delete(db_cart_item)
        await db.commit()
        return await ResponseHandler.delete_success(
            "product remove from cart", db_cart_item.id, db_cart_item
        )

    @staticmethod
    async def get_limited_user_product(
        db: AsyncSession, user_id: int, page: int, limit: int
    ):
        result = await db.execute(
            select(Cart)
            .where(Cart.user_id == user_id)
            .order_by(Cart.created_at.desc())
            .options(selectinload(Cart.cart_items))
        )

        cart = result.scalars().first()

        if not cart:
            return []

        offset = (page - 1) * limit
        items = cart.cart_items[offset : offset + limit]

        book_ids = [item.book_id for item in items]
        return {"message": f"Page {page} with {limit} product", "data": book_ids}

    @staticmethod
    async def get_user_cart_id(db: AsyncSession, user_id: int) -> ApiResponse[CartRead]:
        result = await db.execute(select(Cart).where(Cart.user_id == user_id))
        cart_obj = result.scalar_one_or_none()
        if cart_obj is None:
            raise HTTPException(
                status_code=404, detail=f"Cart for user {user_id} not found"
            )

        return ApiResponse(
            message=f"Cart id from user {user_id}",
            data=CartRead.model_validate(cart_obj, from_attributes=True),
        )
