from fastapi import APIRouter, Depends
from src.schemas.carts import CartItemCreate, CartRead
from src.services.carts import CartService
from src.db.database import get_db
from src.core.pagination import Pagination
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.dto import ApiResponse


carts_router = APIRouter(prefix="/users", tags=["Carts"])


@carts_router.get("/{user_id}/cart/products")
async def get_user_product_limited(
    user_id: int, db: AsyncSession = Depends(get_db), pagination: Pagination = Depends()
):
    return await CartService.get_limited_user_product(
        db, user_id, pagination.page, pagination.limit
    )


@carts_router.post("{user_id}/cart/products")
async def product_to_cart(
    user_id: int, product: CartItemCreate, db: AsyncSession = Depends(get_db)
):
    return await CartService.add_product_to_cart(db, user_id, product)


@carts_router.get("/{user_id}/cart", response_model=ApiResponse[CartRead])
async def get_user_cart(
    user_id: int, db: AsyncSession = Depends(get_db)
) -> ApiResponse[CartRead]:
    return await CartService.get_user_cart_id(db, user_id)
