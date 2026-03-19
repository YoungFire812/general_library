from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.lockers import LockerCreate, LockerRead
from src.db.database import get_db
from src.services.lockers import LockerService
from src.core.deps import dev_verify_admin
from src.schemas.users import UserRead
from typing import List


lockers_router = APIRouter(prefix="/lockers", tags=["Lockers"])


@lockers_router.post("", response_model=LockerRead, status_code=201)
async def create_locker(
    locker_data: LockerCreate,
    db: AsyncSession = Depends(get_db),
    _admin: UserRead = Depends(dev_verify_admin),
) -> LockerRead:
    return await LockerService.create_locker(db, locker_data)


@lockers_router.get("/{locker_id}", response_model=LockerRead)
async def get_one_locker(
    locker_id: int, db: AsyncSession = Depends(get_db)
) -> LockerRead:
    return await LockerService.get_locker(db, locker_id)


@lockers_router.get("", response_model=List[LockerRead])
async def get_all_lockers(
    db: AsyncSession = Depends(get_db),
) -> List[LockerRead]:
    return await LockerService.get_all_lockers(db)
