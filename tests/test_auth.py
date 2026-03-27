import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from src.services.auth import AuthService
from src.schemas.auth import UserCreate, UserLogin
from src.schemas.users import UserRead
from src.models.models import User, Cart
from unittest.mock import AsyncMock
from datetime import datetime, timezone


@pytest.mark.asyncio
class TestUserRegistration:
    async def test_successful_registration(self, db_session):
        data = UserCreate(
            username="newuser",
            email="newuser@mail.com",
            password="securepass123",
            full_name="New User"
        )
        user = await AuthService.user_registration(db_session, data)
        assert isinstance(user, UserRead)
        assert user.username == data.username
        assert user.email == data.email

        assert not hasattr(user, "password")

    async def test_duplicate_email_or_username(self, db_session):
        existing_user = db_session.add(User(
            username="existing",
            email="existing@mail.com",
            password="hashed",
            full_name="Existing User",
            carts=Cart()
        ))
        await db_session.flush()

        data = UserCreate(
            username="existing",
            email="existing@mail.com",
            password="anotherpass123",
            full_name="Duplicate User"
        )
        with pytest.raises(IntegrityError):
            await AuthService.user_registration(db_session, data)

@pytest.mark.asyncio
class TestUserLogin:
    async def test_successful_login_with_email(self, db_session, test_user_first):
        login_data = UserLogin(login=test_user_first.email, password="vasilikrutoi")
        response = await AuthService.user_login(db_session, login_data)
        assert response.status_code == 200
        assert "set-cookie" in response.headers
        assert "refresh_token=" in response.headers["set-cookie"]

    async def test_successful_login_with_username(self, db_session, test_user_first):
        login_data = UserLogin(login=test_user_first.username, password="vasilikrutoi")
        response = await AuthService.user_login(db_session, login_data)
        assert response.status_code == 200

    async def test_failed_login_wrong_password(self, db_session, test_user_first):
        login_data = UserLogin(login=test_user_first.username, password="wrongpass")
        with pytest.raises(HTTPException) as exc:
            await AuthService.user_login(db_session, login_data)
        assert exc.value.status_code == 401

    async def test_failed_login_deleted_user(self, db_session, test_user_first):
        test_user_first.deleted_at = datetime.now(timezone.utc)
        await db_session.flush()
        login_data = UserLogin(login=test_user_first.username, password="vasilikrutoi")
        with pytest.raises(HTTPException) as exc:
            await AuthService.user_login(db_session, login_data)
        assert exc.value.status_code == 401

    async def test_failed_login_user_not_exist(self, db_session):
        login_data = UserLogin(login="unknown", password="anypassword")
        with pytest.raises(HTTPException) as exc:
            await AuthService.user_login(db_session, login_data)
        assert exc.value.status_code == 401

@pytest.mark.asyncio
class TestRefreshToken:
    async def test_refresh_successful(self, db_session, test_user_first):
        login_response = await AuthService.user_login(db_session, UserLogin(
            login=test_user_first.username, password="vasilikrutoi"
        ))
        set_cookie_header = login_response.headers["set-cookie"]
        refresh_token = set_cookie_header.split("refresh_token=")[1].split(";")[0]

        mock_request = AsyncMock()
        mock_request.cookies = {"refresh_token": refresh_token}

        response = await AuthService.refresh(db_session, mock_request)
        assert response.status_code == 200
        assert "set-cookie" in response.headers
        assert "refresh_token=" in response.headers["set-cookie"]

    async def test_refresh_missing_token(self, db_session):
        mock_request = AsyncMock()
        mock_request.cookies = {}
        with pytest.raises(HTTPException) as exc:
            await AuthService.refresh(db_session, mock_request)
        assert exc.value.status_code == 401

    async def test_refresh_invalid_token(self, db_session):
        mock_request = AsyncMock()
        mock_request.cookies = {"refresh_token": "invalid.token.here"}
        with pytest.raises(HTTPException) as exc:
            await AuthService.refresh(db_session, mock_request)
        assert exc.value.status_code == 401