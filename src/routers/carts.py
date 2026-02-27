from fastapi import APIRouter, Depends
from src.schemas.carts import CartItemCreate, CartRead, CartItemRead
from src.services.carts import CartService
from src.db.database import get_db
from src.core.deps import Pagination
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.dto import ApiResponse
from src.core.deps import get_current_user_id, dev_verify_user


carts_router = APIRouter(prefix="/users", tags=["Carts"])


@carts_router.get("/{user_id}/cart/products")
async def get_limited_user_product(
        user_id: int = Depends(dev_verify_user),
        db: AsyncSession = Depends(get_db),
        pagination: Pagination = Depends()):
    return await CartService.get_limited_user_product(
        db, user_id, pagination.page, pagination.limit
    )

@carts_router.post("/cart/products", response_model=ApiResponse[CartItemRead], status_code=201)
async def product_to_cart(
        product: CartItemCreate,
        db: AsyncSession = Depends(get_db),
        user_id: int = Depends(dev_verify_user)) -> ApiResponse[CartItemRead]:
    return await CartService.add_product_to_cart(db, user_id, product)


@carts_router.get("/{user_id}/cart", response_model=ApiResponse[CartRead])
async def get_user_cart(
        user_id: int = Depends(dev_verify_user),
        db: AsyncSession = Depends(get_db)) -> ApiResponse[CartRead]:
    return await CartService.get_user_cart(db, user_id)
