from fastapi import APIRouter, Depends
from src.schemas.carts import CartItemCreate, CartRead, CartItemRead
from src.services.carts import CartService
from src.db.database import get_db
from src.core.deps import Pagination
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.deps import dev_get_current_user
from src.schemas.users import UserRead


carts_router = APIRouter(prefix="/users", tags=["Carts"])


@carts_router.get("/{user_id}/cart/products")
async def get_limited_user_product(
    user: UserRead = Depends(dev_get_current_user),
    db: AsyncSession = Depends(get_db),
    pagination: Pagination = Depends(),
):
    return await CartService.get_limited_user_product(
        db, user.id, pagination.limit, pagination.offset
    )


@carts_router.post("/cart/products", response_model=CartItemRead, status_code=201)
async def product_to_cart(
    product: CartItemCreate,
    db: AsyncSession = Depends(get_db),
    user: UserRead = Depends(dev_get_current_user),
) -> CartItemRead:
    return await CartService.add_product_to_cart(db, user.id, product)


@carts_router.get("/{user_id}/cart", response_model=CartRead)
async def get_user_cart(
    user: UserRead = Depends(dev_get_current_user), db: AsyncSession = Depends(get_db)
) -> CartRead:
    return await CartService.get_user_cart(db, user.id)
