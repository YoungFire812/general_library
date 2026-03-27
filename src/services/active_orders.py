from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.users import UserRead
from src.schemas.active_orders import ActiveOrderCreate, ActiveOrderRead, OrderStatus
from fastapi import HTTPException
from src.models.models import ActiveOrder, Book, Locker
from sqlalchemy import select, func, text, update, or_
from typing import List
from loguru import logger
from enum import Enum


class CancelReason(str, Enum):
    delivery_cancel = "delivery_cancel"
    user_cancel = "user_cancel"


class ActiveOrderService:
    @staticmethod
    async def next_status(db_active_order: ActiveOrder):
        old_status = db_active_order.status
        if db_active_order.status == "waiting_drop":
            db_active_order.status = "delivery"
            db_active_order.user1_status = False
            db_active_order.user2_status = False
        elif db_active_order.status == "waiting_pickup":
            db_active_order.status = "completed"
            db_active_order.finished_at = func.now()
        elif db_active_order.status == "waiting_cancelled":
            db_active_order.status = "cancelled"
            db_active_order.finished_at = func.now()
        else:
            logger.warning("Invalid order status transition", order_id=db_active_order.id, current_status=db_active_order.status)
            raise HTTPException(409, "invalid order status transition")

        logger.info("Order status updated", order_id=db_active_order.id, old_status=old_status, new_status=db_active_order.status)

    @staticmethod
    async def release_lockers(db: AsyncSession, locker_id: int):
        await db.execute(
            update(Locker)
            .where(Locker.id == locker_id)
            .values(available_slots=Locker.available_slots + 1)
        )

        logger.info("Locker released", locker_id=locker_id)

    @staticmethod
    async def confirm_delivery(db: AsyncSession, order_id: int, user: UserRead):
        if user.role != "deliveryman":
            logger.info("invalid user role for delivery", order_id=order_id)
            raise HTTPException(403, "not enough permission")

        result = await db.execute(
            select(ActiveOrder).where(ActiveOrder.id == order_id).with_for_update()
        )

        db_active_order = result.scalar_one_or_none()
        if db_active_order is None:
            logger.info("Order not found for delivery", order_id=order_id)
            raise HTTPException(404, "order with this id is not found")

        if db_active_order.status != "delivery":
            logger.info("Order not int delivery status", order_id=order_id)
            raise HTTPException(409, "order is not in delivery status")

        db_active_order.status = "waiting_pickup"
        db_active_order.time_deadline = func.now() + text("interval '14 days'")

        await db.execute(
            update(Book)
            .where(Book.id == db_active_order.user1_book_id)
            .values(owner_id=db_active_order.user2_id)
        )

        await db.execute(
            update(Book)
            .where(Book.id == db_active_order.user2_book_id)
            .values(owner_id=db_active_order.user1_id)
        )

        logger.info("Delivery confirmed", order_id=order_id, deliveryman_id=user.id)

    @staticmethod
    async def process_expired_orders(db: AsyncSession, batch_size: int = 50):
        while True:
            result = await db.execute(
                select(ActiveOrder)
                .where(
                    ActiveOrder.status.in_(["waiting_pickup", "waiting_cancelled"]),
                    ActiveOrder.time_deadline < func.now(),
                )
                .order_by(ActiveOrder.id)
                .limit(batch_size)
                .with_for_update()
            )

            orders = result.scalars().all()
            if not orders:
                break

            for order in orders:
                if not order.user1_status:
                    await ActiveOrderService.release_lockers(
                        db, order.user1_locker_id
                    )
                if not order.user2_status:
                    await ActiveOrderService.release_lockers(
                        db, order.user2_locker_id
                    )

                await ActiveOrderService.next_status(order)
                logger.info("Expired order processed", order_id=order.id, new_status=order.status, cancel_reason="pickup_cancel")

        while True:
            result = await db.execute(
                select(ActiveOrder)
                .where(
                    ActiveOrder.status == "waiting_drop",
                    ActiveOrder.time_deadline < func.now(),
                )
                .order_by(ActiveOrder.id)
                .limit(batch_size)
            )
            expired_drop_orders = result.scalars().all()
            if not expired_drop_orders:
                break

            for order in expired_drop_orders:
                await ActiveOrderService.time_cancel_active_order(db, order.id)
                logger.info("Expired order processed", order_id=order.id, new_status=order.status, cancel_reason="drop_cancel")

    @staticmethod
    async def confirm_drop_pickup(db: AsyncSession, order_id: int, user: UserRead):
        result = await db.execute(
            select(ActiveOrder).where(ActiveOrder.id == order_id).with_for_update()
        )

        db_active_order = result.scalar_one_or_none()
        if db_active_order is None:
            logger.warning("Drop/pickup confirm failed, order not found", order_id=order_id)
            raise HTTPException(404, "order with this id is not found")

        if db_active_order.status not in ("waiting_drop", "waiting_pickup", "waiting_cancelled"):
            logger.warning("Drop/pickup confirm failed, wrong status", order_id=order_id, current_status=db_active_order.status)
            raise HTTPException(409, "order is not in right status")

        if db_active_order.user1_id == user.id:
            if db_active_order.user1_status:
                logger.warning("Order status already confimed", order_id=order_id)
                raise HTTPException(409, "already confirmed")

            db_active_order.user1_status = True

            if db_active_order.status in ("waiting_pickup", "waiting_cancelled"):
                await ActiveOrderService.release_lockers(
                    db, db_active_order.user1_locker_id
                )
            if db_active_order.user2_status:
                await ActiveOrderService.next_status(db_active_order)

        elif db_active_order.user2_id == user.id:
            if db_active_order.user2_status:
                logger.warning("Order status already confimed", order_id=order_id)
                raise HTTPException(409, "already confirmed")

            db_active_order.user2_status = True

            if db_active_order.status in ("waiting_pickup", "waiting_cancelled"):
                await ActiveOrderService.release_lockers(
                    db, db_active_order.user2_locker_id
                )
            if db_active_order.user1_status:
                await ActiveOrderService.next_status(db_active_order)

        else:
            logger.warning("Not enough permission for order", order_id=order_id)
            raise HTTPException(403, "not enough permission")

        logger.info("Drop/pickup confirmed", order_id=order_id)

    @staticmethod
    async def select_locker(
        db: AsyncSession, order_id: int, user: UserRead, locker_id: int
    ):
        result = await db.execute(
            select(ActiveOrder).where(ActiveOrder.id == order_id).with_for_update()
        )

        db_active_order = result.scalar_one_or_none()
        if db_active_order is None:
            logger.warning("Select locker failed, order not found", order_id=order_id)
            raise HTTPException(404, "order not found")

        if db_active_order.status != "waiting_drop":
            logger.warning("Select locker failed, invalid status", order_id=order_id, status=db_active_order.status)
            raise HTTPException(409, "invalid order status")

        if user.id not in (db_active_order.user1_id, db_active_order.user2_id):
            raise HTTPException(403, "not enough permission")

        if db_active_order.user1_id == user.id:
            work_locker_id = db_active_order.user1_locker_id
        else:
            work_locker_id = db_active_order.user2_locker_id

        if work_locker_id == locker_id:
            logger.warning("Select locker failed, locker already taken", order_id=order_id, locker_id=locker_id)
            raise HTTPException(409, "Locker already taken")

        result = await db.execute(
            update(Locker)
            .where(Locker.id == locker_id, Locker.available_slots > 0)
            .values(available_slots=Locker.available_slots - 1)
            .returning(Locker.id)
        )

        locker_id_db = result.scalar_one_or_none()

        if locker_id_db is None:
            logger.warning("Select locker failed, locker full or not found", locker_id=locker_id)
            raise HTTPException(409, "locker is full or not found")

        if work_locker_id is not None:
            await ActiveOrderService.release_lockers(db, work_locker_id)

        if db_active_order.user1_id == user.id:
            db_active_order.user1_locker_id = locker_id
        else:
            db_active_order.user2_locker_id = locker_id

        logger.info("Locker selected", order_id=order_id, locker_id=locker_id)

    @staticmethod
    async def create_order(
        db: AsyncSession, data: ActiveOrderCreate
    ) -> ActiveOrderRead:
        db_order = ActiveOrder(**data.model_dump())
        db.add(db_order)
        await db.flush()
        await db.refresh(db_order)

        logger.info("Active order created", order_id=db_order.id)
        return ActiveOrderRead.model_validate(db_order)

    @staticmethod
    async def get_active_order(
        db: AsyncSession, order_id: int, user: UserRead
    ) -> ActiveOrderRead:
        result = await db.execute(
            select(ActiveOrder).where(
                ActiveOrder.id == order_id,
                or_(ActiveOrder.user1_id == user.id, ActiveOrder.user2_id == user.id),
            )
        )

        db_active_order = result.scalar_one_or_none()
        if db_active_order is None:
            logger.warning("Get active order failed, order not found", order_id=order_id)
            raise HTTPException(404, "order not found")

        logger.info("Active order retrieved", order_id=order_id)
        return ActiveOrderRead.model_validate(db_active_order)

    @staticmethod
    async def get_orders_by_user(
        db: AsyncSession, user: UserRead, limit: int, offset: int
    ) -> List[ActiveOrderRead]:
        result = await db.execute(
            select(ActiveOrder)
            .where(
                or_(ActiveOrder.user1_id == user.id, ActiveOrder.user2_id == user.id)
            )
            .order_by(ActiveOrder.id.desc())
            .limit(limit)
            .offset(offset)
        )

        db_active_orders = result.scalars().all()

        if not db_active_orders:
            logger.warning("No active orders found for user")
        else:
            logger.info("Fetched orders for user", count=len(db_active_orders))

        return [ActiveOrderRead.model_validate(db_order) for db_order in db_active_orders]

    @staticmethod
    async def time_cancel_active_order(db: AsyncSession, order_id: int):
        result = await db.execute(
            select(ActiveOrder).where(ActiveOrder.id == order_id).with_for_update()
        )

        db_active_order = result.scalar_one_or_none()
        if db_active_order is None:
            logger.warning("Time cancel failed, order not found", order_id=order_id)
            raise HTTPException(404, "order is not found")

        if db_active_order.status != "waiting_drop":
            logger.warning("Time cancel failed, invalid status", order_id=order_id, status=db_active_order.status)
            raise HTTPException(409, "cannot cancel this status")

        user1_dropped = db_active_order.user1_status
        user2_dropped = db_active_order.user2_status

        if not user1_dropped and not user2_dropped:
            db_active_order.status = "cancelled"
            db_active_order.cancel_reason = "time_cancel"
            db_active_order.finished_at = func.now()
            logger.info("Order cancelled due to time expiration", order_id=order_id)
        elif user1_dropped and user2_dropped:
            await ActiveOrderService.next_status(db_active_order)
            logger.info("Order status advanced after time check", order_id=order_id, new_status=db_active_order.status)
        else:
            db_active_order.status = "waiting_cancelled"
            db_active_order.cancel_reason = "time_cancel"
            db_active_order.time_deadline = func.now() + text("interval '14 days'")
            logger.info("Order moved to waiting_cancelled due to partial drop", order_id=order_id)

    @staticmethod
    async def cancel_active_order(
        db: AsyncSession, user: UserRead, order_id: int, cancel_reason: CancelReason
    ):
        result = await db.execute(
            select(ActiveOrder)
            .where(
                ActiveOrder.id == order_id,
                or_(
                    ActiveOrder.user1_id == user.id, ActiveOrder.user2_id == user.id
                ),
            )
            .with_for_update()
        )

        db_active_order = result.scalar_one_or_none()
        if db_active_order is None:
            logger.warning("Cancel order failed, order not found", order_id=order_id)
            raise HTTPException(404, "order is not found")

        if db_active_order.status not in ("waiting_drop", "delivery"):
            logger.warning("Cancel order failed, invalid status", order_id=order_id, status=db_active_order.status)
            raise HTTPException(409, "cannot cancel this status")

        if (
            db_active_order.status == "delivery"
            and cancel_reason == "delivery_cancel"
        ):
            if user.role != "deliveryman":
                logger.warning("Cancel order failed, not deliveryman", order_id=order_id)
                raise HTTPException(403, "not enough permission")

            db_active_order.status = "waiting_cancelled"
            db_active_order.cancel_reason = cancel_reason
            db_active_order.time_deadline = func.now() + text("interval '14 days'")

            db_active_order.user1_status = False
            db_active_order.user2_status = False

            logger.info("Order delivery cancelled", order_id=order_id)

        elif (
            db_active_order.status == "waiting_drop"
            and cancel_reason == "user_cancel"
        ):
            user1_dropped = db_active_order.user1_status
            user2_dropped = db_active_order.user2_status

            is_user1 = user.id == db_active_order.user1_id

            if (is_user1 and user1_dropped) or (not is_user1 and user2_dropped):
                logger.warning("Cancel order failed, user already dropped book", order_id=order_id)
                raise HTTPException(409, "you already dropped book")

            if not user1_dropped and not user2_dropped:
                db_active_order.status = "cancelled"
                db_active_order.cancel_reason = cancel_reason
                db_active_order.finished_at = func.now()
                logger.info("Order cancelled by user", order_id=order_id)
            elif user1_dropped and user2_dropped:
                logger.warning("Cancel order failed, both books already dropped", order_id=order_id)
                raise HTTPException(409, "books already dropped")
            else:
                db_active_order.status = "waiting_cancelled"
                db_active_order.cancel_reason = cancel_reason
                db_active_order.time_deadline = func.now() + text(
                    "interval '14 days'"
                )

                logger.info("Order moved to waiting_cancelled due to partial drop", order_id=order_id)

        else:
            logger.warning("Cancel order failed, invalid combination of status and reason", order_id=order_id, status=db_active_order.status, cancel_reason=cancel_reason)
            raise HTTPException(409, "invalid cancel_reason and status")
