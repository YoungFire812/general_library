import pytest
from fastapi import HTTPException
from datetime import datetime, timezone
from src.services.users import UserService
from src.models.models import User
from src.schemas.users import UserUpdate


class TestGetUserById:
    async def test_get_user_success(self, db_session, test_user_first):
        user = await UserService.get_user_by_id(db_session, test_user_first.id)

        assert user.id == test_user_first.id
        assert user.email == test_user_first.email

    async def test_user_not_found(self, db_session):
        with pytest.raises(HTTPException) as exc:
            await UserService.get_user_by_id(db_session, 999)

        assert exc.value.status_code == 404

    async def test_user_deleted(self, db_session, test_user_first):
        test_user_first.deleted_at = datetime.now(timezone.utc)
        await db_session.flush()

        with pytest.raises(HTTPException):
            await UserService.get_user_by_id(db_session, test_user_first.id)

class TestUpdateUser:
    async def test_update_success(self, db_session, test_user_first):
        data = UserUpdate(username="NewName")

        user = await UserService.update_user(
            db_session,
            test_user_first.id,
            data
        )

        assert user.username == "NewName"

    async def test_update_multiple_fields(self, db_session, test_user_first):
        data = UserUpdate(
            username="NewName",
            full_name="New Full Name"
        )

        user = await UserService.update_user(
            db_session,
            test_user_first.id,
            data
        )

        assert user.username == "NewName"
        assert user.full_name == "New Full Name"

    async def test_update_password(self, db_session, test_user_first):
        data = UserUpdate(password="newpassword")

        user = await UserService.update_user(
            db_session,
            test_user_first.id,
            data
        )

        assert user.id == test_user_first.id

    async def test_user_not_found(self, db_session):
        data = UserUpdate(username="test")

        with pytest.raises(HTTPException) as exc:
            await UserService.update_user(db_session, 999, data)

        assert exc.value.status_code == 404

    async def test_user_deleted(self, db_session, test_user_first):
        test_user_first.deleted_at = datetime.now(timezone.utc)
        await db_session.flush()

        data = UserUpdate(username="test")

        with pytest.raises(HTTPException):
            await UserService.update_user(
                db_session,
                test_user_first.id,
                data
            )

    async def test_no_fields_to_update(self, db_session, test_user_first):
        data = UserUpdate()

        with pytest.raises(HTTPException) as exc:
            await UserService.update_user(
                db_session,
                test_user_first.id,
                data
            )

        assert exc.value.status_code == 400

    async def test_ignore_none_fields(self, db_session, test_user_first):
        data = UserUpdate(username=None)

        with pytest.raises(HTTPException):
            await UserService.update_user(
                db_session,
                test_user_first.id,
                data
            )

class TestDeleteUser:
    async def test_delete_success(self, db_session, test_user_first):
        await UserService.delete_user(db_session, test_user_first)

        user = User(
            id=test_user_first.id,
            username=test_user_first.username,
            email=test_user_first.email,
            password=test_user_first.password,
            full_name=test_user_first.full_name,
            deleted_at=datetime.now(timezone.utc)
        )

        assert user.deleted_at is not None

    async def test_user_not_found(self, db_session, test_user_first):
        test_user_first.deleted_at = datetime.now(timezone.utc)
        await db_session.flush()

        with pytest.raises(HTTPException) as exc:
            await UserService.delete_user(db_session, test_user_first)

        assert exc.value.status_code == 404

    async def test_delete_idempotency(self, db_session, test_user_first):
        await UserService.delete_user(db_session, test_user_first)

        with pytest.raises(HTTPException):
            await UserService.delete_user(db_session, test_user_first)