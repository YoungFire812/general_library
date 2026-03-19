from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from src.schemas.lockers import LockerCreate, LockerRead
from src.models.models import Locker
from src.core.sqlErrors import is_error, UNIQUE_VIOLATION
from fastapi import HTTPException
from typing import List


class LockerService:
    @staticmethod
    async def create_locker(db: AsyncSession, data: LockerCreate) -> LockerRead:
        payload = data.model_dump()

        db_locker = Locker(**payload)
        db.add(db_locker)
        try:
            await db.commit()
            await db.refresh(db_locker)
        except IntegrityError as e:
            if await is_error(e, UNIQUE_VIOLATION):
                raise HTTPException(
                    409, "Locker with this coordinates is already exists"
                )
            else:
                raise

        return LockerRead.model_validate(db_locker)

    @staticmethod
    async def get_locker(db: AsyncSession, locker_id: int) -> LockerRead:
        result = await db.execute(select(Locker).where(Locker.id == locker_id))

        db_locker = result.scalar_one_or_none()
        if db_locker is None:
            raise HTTPException(404, "Locker not found")

        return LockerRead.model_validate(db_locker)

    @staticmethod
    async def get_all_lockers(db: AsyncSession) -> List[LockerRead]:
        result = await db.execute(select(Locker))

        db_lockers = result.scalars().all()
        if not db_lockers:
            raise HTTPException(404, "Lockers not found")

        return [LockerRead.model_validate(db_locker) for db_locker in db_lockers]
