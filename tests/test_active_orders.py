from src.services.active_orders import ActiveOrderService
import pytest
from fastapi import HTTPException
from sqlalchemy import select
from src.models.models import ActiveOrder, Locker
from datetime import datetime, timezone
from src.schemas.active_orders import ActiveOrderCreate, ActiveOrderRead, CancelReason, OrderStatus


@pytest.mark.asyncio
class TestActiveOrderNextStatus:
    async def test_waiting_drop_to_delivery(self, db_session, user_factory, book_factory):
        user1 = await user_factory()
        user2 = await user_factory()
        book1 = await book_factory(owner_id=user1.id)
        book2 = await book_factory(owner_id=user2.id)

        order = ActiveOrder(
            user1_id=user1.id,
            user2_id=user2.id,
            user1_book_id=book1.id,
            user2_book_id=book2.id,
            status="waiting_drop",
            user1_status=True,
            user2_status=True
        )
        db_session.add(order)
        await db_session.flush()
        await db_session.refresh(order)

        await ActiveOrderService.next_status(order)

        assert order.status == "delivery"
        assert order.user1_status is False
        assert order.user2_status is False

    async def test_waiting_pickup_to_completed(self, db_session, user_factory, book_factory):
        user1 = await user_factory()
        user2 = await user_factory()
        book1 = await book_factory(owner_id=user1.id)
        book2 = await book_factory(owner_id=user2.id)

        order = ActiveOrder(
            user1_id=user1.id,
            user2_id=user2.id,
            user1_book_id=book1.id,
            user2_book_id=book2.id,
            status="waiting_pickup"
        )
        db_session.add(order)
        await db_session.flush()
        await db_session.refresh(order)

        await ActiveOrderService.next_status(order)

        assert order.status == "completed"
        assert order.finished_at is not None

    async def test_waiting_cancelled_to_cancelled(self, db_session, user_factory, book_factory):
        user1 = await user_factory()
        user2 = await user_factory()
        book1 = await book_factory(owner_id=user1.id)
        book2 = await book_factory(owner_id=user2.id)

        order = ActiveOrder(
            user1_id=user1.id,
            user2_id=user2.id,
            user1_book_id=book1.id,
            user2_book_id=book2.id,
            status="waiting_cancelled",
        )
        db_session.add(order)
        await db_session.flush()
        await db_session.refresh(order)

        await ActiveOrderService.next_status(order)

        assert order.status == "cancelled"
        assert order.finished_at is not None

    async def test_invalid_status_raises_exception(self, db_session, user_factory, book_factory):
        user1 = await user_factory()
        user2 = await user_factory()
        book1 = await book_factory(owner_id=user1.id)
        book2 = await book_factory(owner_id=user2.id)

        order = ActiveOrder(
            user1_id=user1.id,
            user2_id=user2.id,
            user1_book_id=book1.id,
            user2_book_id=book2.id,
            status="delivery",
        )
        db_session.add(order)
        await db_session.flush()
        await db_session.refresh(order)

        with pytest.raises(HTTPException) as exc_info:
            await ActiveOrderService.next_status(order)
        assert exc_info.value.status_code == 409
        assert "invalid order status transition" in exc_info.value.detail


@pytest.mark.asyncio
class TestLockerReleaseLockers:
    async def test_release_locker_increments_slots(self, db_session):
        locker = Locker(
            name="Test Locker",
            address="123 Test St",
            available_slots=2,
            lat=10.0,
            lng=20.0,
            is_active=True
        )
        db_session.add(locker)
        await db_session.flush()
        await db_session.refresh(locker)

        original_slots = locker.available_slots

        await ActiveOrderService.release_lockers(db_session, locker.id)
        await db_session.refresh(locker)

        assert locker.available_slots == original_slots + 1

    async def test_release_nonexistent_locker_does_nothing(self, db_session):
        non_existent_id = 999999

        result = await db_session.execute(select(Locker).where(Locker.id == non_existent_id))
        locker = result.scalar_one_or_none()
        assert locker is None

        await ActiveOrderService.release_lockers(db_session, non_existent_id)


@pytest.mark.asyncio
class TestConfirmDelivery:
    async def test_successful_delivery(self, db_session, user_factory, book_factory):
        deliveryman = await user_factory(role="deliveryman")
        user1 = await user_factory()
        user2 = await user_factory()
        book1 = await book_factory(owner_id=user1.id)
        book2 = await book_factory(owner_id=user2.id)

        order = ActiveOrder(
            user1_id=user1.id,
            user2_id=user2.id,
            user1_book_id=book1.id,
            user2_book_id=book2.id,
            status="delivery"
        )
        db_session.add(order)
        await db_session.flush()
        await db_session.refresh(order)

        await ActiveOrderService.confirm_delivery(db_session, order.id, deliveryman)

        await db_session.refresh(order)
        await db_session.refresh(book1)
        await db_session.refresh(book2)

        assert order.status == "waiting_pickup"
        assert abs((order.time_deadline - datetime.now(timezone.utc)).days - 14) <= 1
        assert book1.owner_id == user2.id
        assert book2.owner_id == user1.id

    async def test_user_not_deliveryman(self, db_session, user_factory):
        non_delivery_user = await user_factory(role="user")
        order_id = 999
        with pytest.raises(HTTPException) as exc:
            await ActiveOrderService.confirm_delivery(db_session, order_id, non_delivery_user)
        assert exc.value.status_code == 403
        assert "not enough permission" in exc.value.detail

    async def test_order_not_found(self, db_session, user_factory):
        deliveryman = await user_factory(role="deliveryman")
        order_id = 999999
        with pytest.raises(HTTPException) as exc:
            await ActiveOrderService.confirm_delivery(db_session, order_id, deliveryman)
        assert exc.value.status_code == 404
        assert "order with this id is not found" in exc.value.detail

    async def test_order_wrong_status(self, db_session, user_factory, book_factory):
        deliveryman = await user_factory(role="deliveryman")
        user1 = await user_factory()
        user2 = await user_factory()
        book1 = await book_factory(owner_id=user1.id)
        book2 = await book_factory(owner_id=user2.id)

        order = ActiveOrder(
            user1_id=user1.id,
            user2_id=user2.id,
            user1_book_id=book1.id,
            user2_book_id=book2.id,
            status="waiting_drop"
        )
        db_session.add(order)
        await db_session.flush()
        await db_session.refresh(order)

        with pytest.raises(HTTPException) as exc:
            await ActiveOrderService.confirm_delivery(db_session, order.id, deliveryman)
        assert exc.value.status_code == 409
        assert "order is not in delivery status" in exc.value.detail


@pytest.mark.asyncio
class TestConfirmDropPickup:
    async def test_order_not_found(self, db_session, user_factory):
        user = await user_factory()
        order_id = 999999
        with pytest.raises(HTTPException) as exc:
            await ActiveOrderService.confirm_drop_pickup(db_session, order_id, user)
        assert exc.value.status_code == 404
        assert "order with this id is not found" in exc.value.detail

    async def test_wrong_status(self, db_session, user_factory, book_factory):
        user1 = await user_factory()
        user2 = await user_factory()
        book1 = await book_factory(owner_id=user1.id)
        book2 = await book_factory(owner_id=user2.id)

        order = ActiveOrder(
            user1_id=user1.id,
            user2_id=user2.id,
            user1_book_id=book1.id,
            user2_book_id=book2.id,
            status="delivery",
        )
        db_session.add(order)
        await db_session.flush()
        await db_session.refresh(order)

        with pytest.raises(HTTPException) as exc:
            await ActiveOrderService.confirm_drop_pickup(db_session, order.id, user1)
        assert exc.value.status_code == 409
        assert "order is not in right status" in exc.value.detail

    async def test_user1_already_confirmed(self, db_session, user_factory, book_factory):
        user1 = await user_factory()
        user2 = await user_factory()
        book1 = await book_factory(owner_id=user1.id)
        book2 = await book_factory(owner_id=user2.id)

        order = ActiveOrder(
            user1_id=user1.id,
            user2_id=user2.id,
            user1_book_id=book1.id,
            user2_book_id=book2.id,
            status="waiting_drop",
            user1_status=True
        )
        db_session.add(order)
        await db_session.flush()
        await db_session.refresh(order)

        with pytest.raises(HTTPException) as exc:
            await ActiveOrderService.confirm_drop_pickup(db_session, order.id, user1)
        assert exc.value.status_code == 409
        assert "already confirmed" in exc.value.detail

    async def test_user2_already_confirmed(self, db_session, user_factory, book_factory):
        user1 = await user_factory()
        user2 = await user_factory()
        book1 = await book_factory(owner_id=user1.id)
        book2 = await book_factory(owner_id=user2.id)

        order = ActiveOrder(
            user1_id=user1.id,
            user2_id=user2.id,
            user1_book_id=book1.id,
            user2_book_id=book2.id,
            status="waiting_drop",
            user2_status=True
        )
        db_session.add(order)
        await db_session.flush()
        await db_session.refresh(order)

        with pytest.raises(HTTPException) as exc:
            await ActiveOrderService.confirm_drop_pickup(db_session, order.id, user2)
        assert exc.value.status_code == 409
        assert "already confirmed" in exc.value.detail

    async def test_user_not_related(self, db_session, user_factory, book_factory):
        user1 = await user_factory()
        user2 = await user_factory()
        other_user = await user_factory()
        book1 = await book_factory(owner_id=user1.id)
        book2 = await book_factory(owner_id=user2.id)

        order = ActiveOrder(
            user1_id=user1.id,
            user2_id=user2.id,
            user1_book_id=book1.id,
            user2_book_id=book2.id,
            status="waiting_drop",
        )
        db_session.add(order)
        await db_session.flush()
        await db_session.refresh(order)

        with pytest.raises(HTTPException) as exc:
            await ActiveOrderService.confirm_drop_pickup(db_session, order.id, other_user)
        assert exc.value.status_code == 403
        assert "not enough permission" in exc.value.detail

    async def test_user1_confirms_waiting_drop(self, db_session, user_factory, book_factory, locker_factory, mocker):
        user1 = await user_factory()
        user2 = await user_factory()
        locker1 = await locker_factory()
        locker2 = await locker_factory()
        book1 = await book_factory(owner_id=user1.id)
        book2 = await book_factory(owner_id=user2.id)

        order = ActiveOrder(
            user1_id=user1.id,
            user2_id=user2.id,
            user1_book_id=book1.id,
            user2_book_id=book2.id,
            status="waiting_drop",
            user1_locker_id=locker1.id,
            user2_locker_id=locker2.id,
            user1_status = False,
            user2_status = False,
        )
        db_session.add(order)
        await db_session.flush()
        await db_session.refresh(order)

        release_lockers_mock = mocker.patch.object(ActiveOrderService, "release_lockers")
        next_status_mock = mocker.patch.object(ActiveOrderService, "next_status")

        await ActiveOrderService.confirm_drop_pickup(db_session, order.id, user1)
        await db_session.flush()
        await db_session.refresh(order)

        assert order.user1_status is True
        release_lockers_mock.assert_not_called()
        next_status_mock.assert_not_called()

    async def test_both_users_confirm_triggers_next_status(self, db_session, user_factory, book_factory, locker_factory, mocker):
        user1 = await user_factory()
        user2 = await user_factory()
        locker = await locker_factory()
        book1 = await book_factory(owner_id=user1.id)
        book2 = await book_factory(owner_id=user2.id)

        order = ActiveOrder(
            user1_id=user1.id,
            user2_id=user2.id,
            user1_book_id=book1.id,
            user2_book_id=book2.id,
            status="waiting_drop",
            user1_locker_id=locker.id,
            user2_locker_id=locker.id,
            user1_status=True
        )
        db_session.add(order)
        await db_session.flush()
        await db_session.refresh(order)

        next_status_mock = mocker.patch.object(ActiveOrderService, "next_status", autospec=True)

        await ActiveOrderService.confirm_drop_pickup(db_session, order.id, user2)
        await db_session.flush()
        await db_session.refresh(order)

        assert order.user2_status is True
        next_status_mock.assert_called_once_with(order)


@pytest.mark.asyncio
class TestSelectLocker:
    async def test_order_not_found(self, db_session, user_factory, locker_factory):
        user = await user_factory()
        locker = await locker_factory()
        with pytest.raises(HTTPException) as exc:
            await ActiveOrderService.select_locker(db_session, 999999, user, locker.id)
        assert exc.value.status_code == 404

    async def test_invalid_status(self, db_session, user_factory, book_factory, locker_factory):
        user1 = await user_factory()
        user2 = await user_factory()
        book1 = await book_factory(owner_id=user1.id)
        book2 = await book_factory(owner_id=user2.id)
        locker = await locker_factory()

        order = ActiveOrder(
            user1_id=user1.id,
            user2_id=user2.id,
            user1_book_id=book1.id,
            user2_book_id=book2.id,
            status="delivery",
        )
        db_session.add(order)
        await db_session.flush()
        await db_session.refresh(order)

        with pytest.raises(HTTPException) as exc:
            await ActiveOrderService.select_locker(db_session, order.id, user1, locker.id)
        assert exc.value.status_code == 409

    async def test_user_no_permission(self, db_session, user_factory, book_factory, locker_factory):
        user1 = await user_factory()
        user2 = await user_factory()
        other_user = await user_factory()
        book1 = await book_factory(owner_id=user1.id)
        book2 = await book_factory(owner_id=user2.id)
        locker = await locker_factory()

        order = ActiveOrder(
            user1_id=user1.id,
            user2_id=user2.id,
            user1_book_id=book1.id,
            user2_book_id=book2.id,
            status="waiting_drop"
        )
        db_session.add(order)
        await db_session.flush()
        await db_session.refresh(order)

        with pytest.raises(HTTPException) as exc:
            await ActiveOrderService.select_locker(db_session, order.id, other_user, locker.id)
        assert exc.value.status_code == 403

    async def test_locker_already_taken_by_user(self, db_session, user_factory, book_factory, locker_factory):
        user1 = await user_factory()
        user2 = await user_factory()
        book1 = await book_factory(owner_id=user1.id)
        book2 = await book_factory(owner_id=user2.id)
        locker = await locker_factory()

        order = ActiveOrder(
            user1_id=user1.id,
            user2_id=user2.id,
            user1_book_id=book1.id,
            user2_book_id=book2.id,
            status="waiting_drop",
            user1_locker_id=locker.id
        )
        db_session.add(order)
        await db_session.flush()
        await db_session.refresh(order)

        with pytest.raises(HTTPException) as exc:
            await ActiveOrderService.select_locker(db_session, order.id, user1, locker.id)
        assert exc.value.status_code == 409

    async def test_locker_full_or_not_found(self, db_session, user_factory, book_factory, locker_factory):
        user1 = await user_factory()
        user2 = await user_factory()
        book1 = await book_factory(owner_id=user1.id)
        book2 = await book_factory(owner_id=user2.id)
        locker = await locker_factory(available_slots=1)
        locker.available_slots = 0
        await db_session.flush()

        order = ActiveOrder(
            user1_id=user1.id,
            user2_id=user2.id,
            user1_book_id=book1.id,
            user2_book_id=book2.id,
            status="waiting_drop"
        )
        db_session.add(order)
        await db_session.flush()
        await db_session.refresh(order)

        with pytest.raises(HTTPException) as exc:
            await ActiveOrderService.select_locker(db_session, order.id, user1, locker.id)
        assert exc.value.status_code == 409

    async def test_success_select_locker_new(self, db_session, user_factory, book_factory, locker_factory, mocker):
        user1 = await user_factory()
        user2 = await user_factory()
        book1 = await book_factory(owner_id=user1.id)
        book2 = await book_factory(owner_id=user2.id)
        old_locker = await locker_factory()
        new_locker = await locker_factory()

        order = ActiveOrder(
            user1_id=user1.id,
            user2_id=user2.id,
            user1_book_id=book1.id,
            user2_book_id=book2.id,
            status="waiting_drop",
            user1_locker_id=old_locker.id
        )
        db_session.add(order)
        await db_session.flush()
        await db_session.refresh(order)

        release_mock = mocker.patch.object(ActiveOrderService, "release_lockers", autospec=True)

        await ActiveOrderService.select_locker(db_session, order.id, user1, new_locker.id)
        await db_session.flush()
        await db_session.refresh(order)

        assert order.user1_locker_id == new_locker.id
        release_mock.assert_called_once_with(db_session, old_locker.id)

    async def test_success_select_locker_first_time(self, db_session, user_factory, book_factory, locker_factory, mocker):
        user1 = await user_factory()
        user2 = await user_factory()
        book1 = await book_factory(owner_id=user1.id)
        book2 = await book_factory(owner_id=user2.id)
        new_locker = await locker_factory()

        order = ActiveOrder(
            user1_id=user1.id,
            user2_id=user2.id,
            user1_book_id=book1.id,
            user2_book_id=book2.id,
            status="waiting_drop"
        )
        db_session.add(order)
        await db_session.flush()
        await db_session.refresh(order)

        release_mock = mocker.patch.object(ActiveOrderService, "release_lockers", autospec=True)

        await ActiveOrderService.select_locker(db_session, order.id, user1, new_locker.id)
        await db_session.flush()
        await db_session.refresh(order)

        assert order.user1_locker_id == new_locker.id
        release_mock.assert_not_called()


@pytest.mark.asyncio
class TestCreateOrder:
    async def test_create_order_success(self, db_session, user_factory, book_factory):
        user1 = await user_factory()
        user2 = await user_factory()

        book1 = await book_factory(owner_id=user1.id)
        book2 = await book_factory(owner_id=user2.id)

        data = ActiveOrderCreate(
            user1_id=user1.id,
            user2_id=user2.id,
            user1_book_id=book1.id,
            user2_book_id=book2.id,
        )

        result = await ActiveOrderService.create_order(db_session, data)

        assert isinstance(result, ActiveOrderRead)
        assert result.user1_id == user1.id
        assert result.user2_id == user2.id
        assert result.user1_book_id == book1.id
        assert result.user2_book_id == book2.id
        assert result.status == OrderStatus.waiting_drop
        assert result.id is not None

    async def test_create_order_default_values(self, db_session, user_factory, book_factory):
        user1 = await user_factory()
        user2 = await user_factory()
        book1 = await book_factory(owner_id=user1.id)
        book2 = await book_factory(owner_id=user2.id)

        data = ActiveOrderCreate(
            user1_id=user1.id,
            user2_id=user2.id,
            user1_book_id=book1.id,
            user2_book_id=book2.id
        )

        result = await ActiveOrderService.create_order(db_session, data)

        assert result.status == OrderStatus.waiting_drop
        assert result.id is not None


@pytest.mark.asyncio
class TestGetActiveOrder:
    async def test_get_active_order_success(self, db_session, user_factory, book_factory):
        user1 = await user_factory()
        user2 = await user_factory()

        book1 = await book_factory(owner_id=user1.id)
        book2 = await book_factory(owner_id=user2.id)

        data = ActiveOrderCreate(
            user1_id=user1.id,
            user2_id=user2.id,
            user1_book_id=book1.id,
            user2_book_id=book2.id,
        )
        order = await ActiveOrderService.create_order(db_session, data)

        result = await ActiveOrderService.get_active_order(db_session, order.id, user1)

        assert isinstance(result, ActiveOrderRead)
        assert result.id == order.id
        assert result.user1_id == user1.id
        assert result.user2_id == user2.id

    async def test_get_active_order_not_found(self, db_session, user_factory):
        user = await user_factory()

        with pytest.raises(HTTPException) as exc:
            await ActiveOrderService.get_active_order(db_session, 9999, user)
        assert exc.value.status_code == 404

    async def test_get_active_order_wrong_user(self, db_session, user_factory, book_factory):
        user1 = await user_factory()
        user2 = await user_factory()
        stranger = await user_factory()

        book1 = await book_factory(owner_id=user1.id)
        book2 = await book_factory(owner_id=user2.id)

        data = ActiveOrderCreate(
            user1_id=user1.id,
            user2_id=user2.id,
            user1_book_id=book1.id,
            user2_book_id=book2.id,
        )
        order = await ActiveOrderService.create_order(db_session, data)

        with pytest.raises(HTTPException) as exc:
            await ActiveOrderService.get_active_order(db_session, order.id, stranger)
        assert exc.value.status_code == 404


@pytest.mark.asyncio
class TestGetOrdersByUser:
    async def test_get_orders_by_user_success(self, db_session, user_factory, book_factory):
        user1 = await user_factory()
        user2 = await user_factory()

        books_user1 = [await book_factory(owner_id=user1.id) for _ in range(5)]
        books_user2 = [await book_factory(owner_id=user2.id) for _ in range(5)]

        orders = []
        for i in range(5):
            data = ActiveOrderCreate(
                user1_id=user1.id,
                user2_id=user2.id,
                user1_book_id=books_user1[i].id,
                user2_book_id=books_user2[i].id,
            )
            order = await ActiveOrderService.create_order(db_session, data)
            orders.append(order)

        result = await ActiveOrderService.get_orders_by_user(db_session, user1, limit=3, offset=0)

        assert len(result) == 3
        assert all(isinstance(o, ActiveOrderRead) for o in result)

    async def test_get_orders_by_user_empty(self, db_session, user_factory):
        user = await user_factory()

        result = await ActiveOrderService.get_orders_by_user(db_session, user, limit=5, offset=0)
        assert result == []

    async def test_get_orders_by_user_offset(self, db_session, user_factory, book_factory):
        user1 = await user_factory()
        user2 = await user_factory()

        books_user1 = [await book_factory(owner_id=user1.id) for _ in range(5)]
        books_user2 = [await book_factory(owner_id=user2.id) for _ in range(5)]

        for i in range(5):
            data = ActiveOrderCreate(
                user1_id=user1.id,
                user2_id=user2.id,
                user1_book_id=books_user1[i].id,
                user2_book_id=books_user2[i].id,
            )
            await ActiveOrderService.create_order(db_session, data)

        result = await ActiveOrderService.get_orders_by_user(db_session, user1, limit=2, offset=2)
        assert len(result) == 2
        assert result[0].id > result[1].id


@pytest.mark.asyncio
class TestTimeCancelActiveOrder:
    async def test_time_cancel_order_not_found(self, db_session):
        invalid_order_id = 99999

        with pytest.raises(HTTPException) as exc:
            await ActiveOrderService.time_cancel_active_order(db_session, invalid_order_id)

        assert exc.value.status_code == 404

    async def test_time_cancel_invalid_status(self, db_session, user_factory, book_factory):
        user1 = await user_factory()
        user2 = await user_factory()
        book1 = await book_factory(owner_id=user1.id)
        book2 = await book_factory(owner_id=user2.id)

        data = ActiveOrderCreate(
            user1_id=user1.id,
            user2_id=user2.id,
            user1_book_id=book1.id,
            user2_book_id=book2.id,
        )
        order = await ActiveOrderService.create_order(db_session, data)

        order_db = await db_session.get(ActiveOrder, order.id)
        order_db.status = "delivery"


        with pytest.raises(HTTPException) as exc:
            await ActiveOrderService.time_cancel_active_order(db_session, order.id)

        assert exc.value.status_code == 409

    async def test_time_cancel_full_cancel(self, db_session, user_factory, book_factory):
        user1 = await user_factory()
        user2 = await user_factory()
        book1 = await book_factory(owner_id=user1.id)
        book2 = await book_factory(owner_id=user2.id)

        data = ActiveOrderCreate(
            user1_id=user1.id,
            user2_id=user2.id,
            user1_book_id=book1.id,
            user2_book_id=book2.id,
        )
        order = await ActiveOrderService.create_order(db_session, data)

        await ActiveOrderService.time_cancel_active_order(db_session, order.id)

        order_db = await db_session.get(ActiveOrder, order.id)
        assert order_db.status == "cancelled"
        assert order_db.cancel_reason == "time_cancel"
        assert order_db.finished_at is not None

    async def test_time_cancel_partial_drop(self, db_session, user_factory, book_factory):
        user1 = await user_factory()
        user2 = await user_factory()
        book1 = await book_factory(owner_id=user1.id)
        book2 = await book_factory(owner_id=user2.id)

        data = ActiveOrderCreate(
            user1_id=user1.id,
            user2_id=user2.id,
            user1_book_id=book1.id,
            user2_book_id=book2.id,
        )
        order = await ActiveOrderService.create_order(db_session, data)

        order_db = await db_session.get(ActiveOrder, order.id)
        order_db.user1_status = True

        await ActiveOrderService.time_cancel_active_order(db_session, order.id)

        order_db = await db_session.get(ActiveOrder, order.id)
        assert order_db.status == "waiting_cancelled"
        assert order_db.cancel_reason == "time_cancel"
        assert order_db.time_deadline is not None

    async def test_time_cancel_both_dropped_next_status(self, db_session, user_factory, book_factory, mocker):
        user1 = await user_factory()
        user2 = await user_factory()
        book1 = await book_factory(owner_id=user1.id)
        book2 = await book_factory(owner_id=user2.id)

        data = ActiveOrderCreate(
            user1_id=user1.id,
            user2_id=user2.id,
            user1_book_id=book1.id,
            user2_book_id=book2.id,
        )
        order = await ActiveOrderService.create_order(db_session, data)

        order_db = await db_session.get(ActiveOrder, order.id)
        order_db.user1_status = True
        order_db.user2_status = True

        next_status_mock = mocker.patch("src.services.active_orders.ActiveOrderService.next_status")

        await ActiveOrderService.time_cancel_active_order(db_session, order.id)

        next_status_mock.assert_called_once_with(order_db)


@pytest.mark.asyncio
class TestCancelActiveOrder:
    async def test_cancel_order_not_found(self, db_session, user_factory):
        user = await user_factory()
        invalid_order_id = 9999

        with pytest.raises(HTTPException) as exc:
            await ActiveOrderService.cancel_active_order(db_session, user, invalid_order_id, CancelReason.user_cancel)

        assert exc.value.status_code == 404

    async def test_cancel_order_invalid_status(self, db_session, user_factory, book_factory):
        user1 = await user_factory()
        user2 = await user_factory()
        book1 = await book_factory(owner_id=user1.id)
        book2 = await book_factory(owner_id=user2.id)
        data = ActiveOrderCreate(user1_id=user1.id, user2_id=user2.id, user1_book_id=book1.id, user2_book_id=book2.id)
        order = await ActiveOrderService.create_order(db_session, data)

        order_db = await db_session.get(ActiveOrder, order.id)
        order_db.status = "completed"


        with pytest.raises(HTTPException) as exc:
            await ActiveOrderService.cancel_active_order(db_session, user1, order.id, CancelReason.user_cancel)

        assert exc.value.status_code == 409

    async def test_delivery_cancel_not_deliveryman(self, db_session, user_factory, book_factory):
        user1 = await user_factory(role="user")
        user2 = await user_factory(role="user")
        book1 = await book_factory(owner_id=user1.id)
        book2 = await book_factory(owner_id=user2.id)
        data = ActiveOrderCreate(user1_id=user1.id, user2_id=user2.id, user1_book_id=book1.id, user2_book_id=book2.id)
        order = await ActiveOrderService.create_order(db_session, data)

        order_db = await db_session.get(ActiveOrder, order.id)
        order_db.status = "delivery"


        with pytest.raises(HTTPException) as exc:
            await ActiveOrderService.cancel_active_order(db_session, user1, order.id, CancelReason.delivery_cancel)

        assert exc.value.status_code == 403

    async def test_delivery_cancel_success(self, db_session, user_factory, book_factory):
        user = await user_factory(role="deliveryman")
        user2 = await user_factory()
        book1 = await book_factory(owner_id=user.id)
        book2 = await book_factory(owner_id=user2.id)
        data = ActiveOrderCreate(user1_id=user.id, user2_id=user2.id, user1_book_id=book1.id, user2_book_id=book2.id)
        order = await ActiveOrderService.create_order(db_session, data)

        order_db = await db_session.get(ActiveOrder, order.id)
        order_db.status = "delivery"

        await ActiveOrderService.cancel_active_order(db_session, user, order.id, CancelReason.delivery_cancel)

        order_db = await db_session.get(ActiveOrder, order.id)
        assert order_db.status == "waiting_cancelled"
        assert order_db.cancel_reason == CancelReason.delivery_cancel
        assert order_db.time_deadline is not None
        assert not order_db.user1_status and not order_db.user2_status

    async def test_user_cancel_full(self, db_session, user_factory, book_factory):
        user1 = await user_factory()
        user2 = await user_factory()
        book1 = await book_factory(owner_id=user1.id)
        book2 = await book_factory(owner_id=user2.id)

        data = ActiveOrderCreate(user1_id=user1.id, user2_id=user2.id, user1_book_id=book1.id, user2_book_id=book2.id)
        order = await ActiveOrderService.create_order(db_session, data)

        await ActiveOrderService.cancel_active_order(db_session, user1, order.id, CancelReason.user_cancel)

        order_db = await db_session.get(ActiveOrder, order.id)
        assert order_db.status == "cancelled"
        assert order_db.cancel_reason == CancelReason.user_cancel
        assert order_db.finished_at is not None

    async def test_user_cancel_partial_drop(self, db_session, user_factory, book_factory):
        user1 = await user_factory()
        user2 = await user_factory()
        book1 = await book_factory(owner_id=user1.id)
        book2 = await book_factory(owner_id=user2.id)

        data = ActiveOrderCreate(user1_id=user1.id, user2_id=user2.id, user1_book_id=book1.id, user2_book_id=book2.id)
        order = await ActiveOrderService.create_order(db_session, data)

        order_db = await db_session.get(ActiveOrder, order.id)
        order_db.user2_status = True

        await ActiveOrderService.cancel_active_order(db_session, user1, order.id, CancelReason.user_cancel)

        order_db = await db_session.get(ActiveOrder, order.id)
        assert order_db.status == "waiting_cancelled"
        assert order_db.cancel_reason == CancelReason.user_cancel
        assert order_db.time_deadline is not None

    async def test_user_cancel_already_dropped(self, db_session, user_factory, book_factory):
        user1 = await user_factory()
        user2 = await user_factory()
        book1 = await book_factory(owner_id=user1.id)
        book2 = await book_factory(owner_id=user2.id)

        data = ActiveOrderCreate(user1_id=user1.id, user2_id=user2.id, user1_book_id=book1.id, user2_book_id=book2.id)
        order = await ActiveOrderService.create_order(db_session, data)

        order_db = await db_session.get(ActiveOrder, order.id)
        order_db.user1_status = True

        with pytest.raises(HTTPException) as exc:
            await ActiveOrderService.cancel_active_order(db_session, user1, order.id, CancelReason.user_cancel)

        assert exc.value.status_code == 409

    async def test_user_cancel_both_dropped(self, db_session, user_factory, book_factory):
        user1 = await user_factory()
        user2 = await user_factory()
        book1 = await book_factory(owner_id=user1.id)
        book2 = await book_factory(owner_id=user2.id)

        data = ActiveOrderCreate(user1_id=user1.id, user2_id=user2.id, user1_book_id=book1.id, user2_book_id=book2.id)
        order = await ActiveOrderService.create_order(db_session, data)

        order_db = await db_session.get(ActiveOrder, order.id)
        order_db.user1_status = True
        order_db.user2_status = True

        with pytest.raises(HTTPException) as exc:
            await ActiveOrderService.cancel_active_order(db_session, user1, order.id, CancelReason.user_cancel)

        assert exc.value.status_code == 409

    async def test_invalid_status_and_reason_combination(self, db_session, user_factory, book_factory):
        user1 = await user_factory()
        user2 = await user_factory()
        book1 = await book_factory(owner_id=user1.id)
        book2 = await book_factory(owner_id=user2.id)

        data = ActiveOrderCreate(user1_id=user1.id, user2_id=user2.id, user1_book_id=book1.id, user2_book_id=book2.id)
        order = await ActiveOrderService.create_order(db_session, data)

        order_db = await db_session.get(ActiveOrder, order.id)
        order_db.status = "waiting_drop"

        with pytest.raises(HTTPException) as exc:
            await ActiveOrderService.cancel_active_order(db_session, user1, order.id, CancelReason.delivery_cancel)

        assert exc.value.status_code == 409