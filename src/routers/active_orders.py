from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_db
from src.services.active_orders import ActiveOrderService
from src.core.deps import dev_get_current_user
from src.schemas.users import UserRead
from src.schemas.active_orders import (
    ActiveOrderRead,
    CancelOrderRequest,
)
from src.schemas.lockers import LockerRequest
from typing import List
from src.core.deps import Pagination


active_orders_router = APIRouter(prefix="/active_orders", tags=["ActiveOrders"])


@active_orders_router.post("/deliver/{order_id}")
async def confirm_delivery(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    user: UserRead = Depends(dev_get_current_user),
):
    return await ActiveOrderService.confirm_delivery(db, order_id, user)


@active_orders_router.get("/{order_id}", response_model=ActiveOrderRead)
async def get_active_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    user: UserRead = Depends(dev_get_current_user),
):
    return await ActiveOrderService.get_active_order(db, order_id, user)


@active_orders_router.get("", response_model=List[ActiveOrderRead])
async def get_orders_by_user(
    db: AsyncSession = Depends(get_db),
    user: UserRead = Depends(dev_get_current_user),
    pagination: Pagination = Depends(),
):
    return await ActiveOrderService.get_orders_by_user(
        db, user, pagination.limit, pagination.offset
    )


@active_orders_router.post("/drop_pickup/{order_id}")
async def confirm_drop_pickup(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    user: UserRead = Depends(dev_get_current_user),
):
    return await ActiveOrderService.confirm_drop_pickup(db, order_id, user)


@active_orders_router.post("/lockers/{order_id}")
async def select_locker(
    order_id: int,
    payload: LockerRequest,
    db: AsyncSession = Depends(get_db),
    user: UserRead = Depends(dev_get_current_user),
):
    return await ActiveOrderService.select_locker(db, order_id, user, payload.locker_id)


@active_orders_router.post("/cancel/{order_id}")
async def cancel_order(
    order_id: int,
    payload: CancelOrderRequest,
    db: AsyncSession = Depends(get_db),
    user: UserRead = Depends(dev_get_current_user),
):
    return await ActiveOrderService.cancel_active_order(
        db, user, order_id, payload.cancel_reason
    )
