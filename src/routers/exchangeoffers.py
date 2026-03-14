from fastapi import APIRouter, Depends
from src.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Literal
from src.core.deps import Pagination, dev_get_current_user
from src.schemas.users import UserRead
from src.schemas.exchangeoffers import ExchangeOfferCreate, ExchangeOfferRead, ExchangeOfferRole
from src.schemas.activeorders import ActiveOrderRead
from src.services.exchangeoffers import ExchangeOfferService


exchange_offers_router = APIRouter(prefix="/offers")

@exchange_offers_router.get("/", tags=["Exchange offers"], response_model=List[ExchangeOfferRead])
async def get_user_offers(
        db: AsyncSession = Depends(get_db),
        pagination: Pagination = Depends(),
        user: UserRead = Depends(dev_get_current_user),
        status: ExchangeOfferRole | None = None,
        direction: Literal["incoming","outgoing"] | None = None
) -> List[ExchangeOfferRead]:
    return await ExchangeOfferService.get_user_offers(db, user.id, pagination.limit, pagination.offset, status, direction)

@exchange_offers_router.get("/{offer_id}", tags=["Exchange offers"], response_model=ExchangeOfferRead)
async def get_one_offer(
        offer_id: int,
        db: AsyncSession = Depends(get_db),
        user: UserRead = Depends(dev_get_current_user)
) -> ExchangeOfferRead:
    return await ExchangeOfferService.get_one_offer(db, user.id, offer_id)

@exchange_offers_router.post("/", tags=["Exchange offers"], response_model=ExchangeOfferRead, status_code=201)
async def create_offer(
        offer: ExchangeOfferCreate,
        db: AsyncSession = Depends(get_db),
        user: UserRead = Depends(dev_get_current_user)
) -> ExchangeOfferRead:
    return await ExchangeOfferService.create_offer(db, user.id, offer)

@exchange_offers_router.post("/{offer_id}/decline", tags=["Exchange offers"])
async def decline_offer(
        offer_id: int,
        db: AsyncSession = Depends(get_db),
        user: UserRead = Depends(dev_get_current_user)
):
    return await ExchangeOfferService.decline_offer(db, offer_id, user.id)

@exchange_offers_router.post("/{offer_id}/accept", tags=["Exchange offers"], response_model=ActiveOrderRead, status_code=201)
async def accept_offer(
        offer_id: int,
        db: AsyncSession = Depends(get_db),
        user: UserRead = Depends(dev_get_current_user)
) -> ActiveOrderRead:
    return await ExchangeOfferService.accept_offer(db, offer_id, user.id)


