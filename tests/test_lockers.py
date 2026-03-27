import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from src.models.models import Locker
from src.schemas.lockers import LockerCreate, LockerRead
from src.services.lockers import LockerService
from pydantic import ValidationError


@pytest.mark.asyncio
class TestCreateLocker:
    async def test_create_locker_success(self, db_session):
        data = LockerCreate(
            name="Locker A",
            address="123 Street",
            available_slots=10,
            lat=55.0,
            lng=37.0
        )
        result = await LockerService.create_locker(db_session, data)
        assert isinstance(result, LockerRead)
        assert result.name == data.name
        assert result.address == data.address
        assert result.available_slots == data.available_slots
        assert result.lat == data.lat
        assert result.lng == data.lng

    async def test_create_locker_missing_fields(self, db_session):
        locker = Locker(
            name=None,
            address=None,
            available_slots=None,
            lat=None,
            lng=None
        )
        db_session.add(locker)
        with pytest.raises(IntegrityError):
            await db_session.flush()

    async def test_create_locker_duplicate_coordinates(self, db_session):
        locker = Locker(
            name="Locker B",
            address="456 Avenue",
            available_slots=5,
            lat=56.0,
            lng=38.0
        )
        db_session.add(locker)
        await db_session.flush()

        duplicate_data = LockerCreate(
            name="Locker C",
            address="789 Road",
            available_slots=7,
            lat=56.0,
            lng=38.0
        )
        with pytest.raises(IntegrityError):
            await LockerService.create_locker(db_session, duplicate_data)

@pytest.mark.asyncio
class TestGetLocker:
    async def test_get_locker_success(self, db_session):
        locker = Locker(
            name="Locker D",
            address="1st Ave",
            available_slots=3,
            lat=50.0,
            lng=30.0
        )
        db_session.add(locker)
        await db_session.flush()

        result = await LockerService.get_locker(db_session, locker.id)
        assert isinstance(result, LockerRead)
        assert result.id == locker.id
        assert result.name == locker.name

    async def test_get_locker_not_found(self, db_session):
        with pytest.raises(HTTPException) as exc:
            await LockerService.get_locker(db_session, locker_id=999)
        assert exc.value.status_code == 404

@pytest.mark.asyncio
class TestGetAllLockers:
    async def test_get_all_lockers_success(self, db_session):
        lockers = [
            Locker(name="Locker E", address="A1", available_slots=3, lat=51.0, lng=31.0),
            Locker(name="Locker F", address="B2", available_slots=7, lat=52.0, lng=32.0)
        ]
        db_session.add_all(lockers)
        await db_session.flush()

        result = await LockerService.get_all_lockers(db_session)
        assert len(result) == len(lockers)
        assert all(isinstance(l, LockerRead) for l in result)

    async def test_get_all_lockers_not_found(self, db_session):
        await db_session.execute(Locker.__table__.delete())
        await db_session.flush()

        with pytest.raises(HTTPException) as exc:
            await LockerService.get_all_lockers(db_session)
        assert exc.value.status_code == 404