from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.schemas.lockers import LockerCreate, LockerRead
from src.models.models import Locker
from fastapi import HTTPException
from typing import List
from loguru import logger


class LockerService:
    @staticmethod
    async def create_locker(db: AsyncSession, data: LockerCreate) -> LockerRead:
        payload = data.model_dump()

        db_locker = Locker(**payload)
        db.add(db_locker)

        await db.commit()
        await db.refresh(db_locker)

        logger.info("Locker created successfully", locker_id=db_locker.id)
        return LockerRead.model_validate(db_locker)

    @staticmethod
    async def get_locker(db: AsyncSession, locker_id: int) -> LockerRead:
        result = await db.execute(select(Locker).where(Locker.id == locker_id))

        db_locker = result.scalar_one_or_none()
        if db_locker is None:
            logger.warning("Locker not found", locker_id=locker_id)
            raise HTTPException(404, "Locker not found")

        logger.info("Locker fetched successfully", locker_id=locker_id)
        return LockerRead.model_validate(db_locker)

    @staticmethod
    async def get_all_lockers(db: AsyncSession) -> List[LockerRead]:
        result = await db.execute(select(Locker))
        db_lockers = result.scalars().all()

        if not db_lockers:
            logger.warning("No lockers found")
            raise HTTPException(404, "Lockers not found")

        logger.info("All lockers fetched successfully", count=len(db_lockers))
        return [LockerRead.model_validate(db_locker) for db_locker in db_lockers]
