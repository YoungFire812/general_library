from src.schemas.exchangeoffers import ExchangeOfferCreate, ExchangeOfferRead, ExchangeOfferRole
from src.schemas.activeorders import ActiveOrderRead
from src.models.models import ExchangeOffer, Book
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from src.core.sqlErrors import is_error, UNIQUE_VIOLATION
from fastapi import HTTPException
from sqlalchemy import select, func, or_
from sqlalchemy.orm import aliased, selectinload
from src.services.users import UserService
from typing import List, Literal


class ExchangeOfferService:
    @staticmethod
    async def get_user_offers(db: AsyncSession, user_id: int, limit: int, offset: int, status: ExchangeOfferRole | None = None, direction: Literal["incoming","outgoing"] | None = None) -> List[ExchangeOfferRead]:
        stmt = (
            select(ExchangeOffer)
            .options(
                selectinload(ExchangeOffer.offered_book).selectinload(Book.category),
                selectinload(ExchangeOffer.requested_book).selectinload(Book.category)
            )
        )
        if direction == "incoming":
            stmt = stmt.where(ExchangeOffer.to_user_id == user_id)
        elif direction == "outgoing":
            stmt = stmt.where(ExchangeOffer.from_user_id == user_id)
        else:
            stmt = stmt.where(
                or_(
                    ExchangeOffer.to_user_id == user_id,
                    ExchangeOffer.from_user_id == user_id
                )
            )

        if status is not None:
            stmt = stmt.where(ExchangeOffer.status == status)

        stmt = (
            stmt
            .order_by(ExchangeOffer.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await db.execute(stmt)
        db_offers = result.scalars().all()
        offers = [ExchangeOfferRead.model_validate(db_offer) for db_offer in db_offers]
        return offers

    @staticmethod
    async def get_one_offer(db: AsyncSession, user_id: int, offer_id: int) -> ExchangeOfferRead:
        result = await db.execute(
            select(ExchangeOffer)
            .options(
                selectinload(ExchangeOffer.offered_book).selectinload(Book.category),
                selectinload(ExchangeOffer.requested_book).selectinload(Book.category)
            )
            .where(
                ExchangeOffer.id == offer_id,
                or_(
                    ExchangeOffer.to_user_id == user_id,
                    ExchangeOffer.from_user_id == user_id
                )
            )
        )
        db_offer = result.scalar_one_or_none()
        if db_offer is None:
            raise HTTPException(404, "Offer not found")

        return ExchangeOfferRead.model_validate(db_offer)

    @staticmethod
    async def create_offer(db: AsyncSession, user_id: int, data: ExchangeOfferCreate) -> ExchangeOfferRead:
        if user_id != data.from_user_id:
            raise HTTPException(403, "Not enough permission!")

        if data.from_user_id == data.to_user_id:
            raise HTTPException(400, "You cannot exchange with yourself")

        if data.offered_book_id == data.requested_book_id:
            raise HTTPException(400, "Books must be different")

        UserService.get_user_by_id(data.to_user_id)

        OfferedBook = aliased(Book)
        RequestedBook = aliased(Book)

        result = await db.execute(
            select(OfferedBook, RequestedBook)
            .where(
                OfferedBook.id == data.offered_book_id,
                OfferedBook.owner_id == data.from_user_id,
                OfferedBook.status == "available",
                RequestedBook.id == data.requested_book_id,
                RequestedBook.owner_id == data.to_user_id,
                RequestedBook.status == "available"
            )
        )

        books = result.first()
        if not books:
            raise HTTPException(404, "Books not found")

        payload = data.model_dump()
        db_offer = ExchangeOffer(**payload)

        db.add(db_offer)

        try:
            await db.commit()
            await db.refresh(db_offer)
        except IntegrityError as e:
            await db.rollback()
            if is_error(e, UNIQUE_VIOLATION):
                raise HTTPException(409, "offer with this data is already exists")
            else:
                raise

        return ExchangeOfferRead.model_validate(db_offer)

    @staticmethod
    async def decline_offer(db: AsyncSession, offer_id: int, user_id: int):
        async with db.begin():
            result = await db.execute(
                select(ExchangeOffer)
                .where(
                    ExchangeOffer.id == offer_id,
                    ExchangeOffer.status == "pending",
                    ExchangeOffer.expires_at > func.now(),
                    or_(
                        ExchangeOffer.to_user_id == user_id,
                        ExchangeOffer.from_user_id == user_id
                    )
                )
                .with_for_update()
            )

            db_offer = result.scalar_one_or_none()

            if db_offer is None:
                raise HTTPException(404, "Offer not found")

            db_offer.status = "declined"
            db_offer.responded_at = func.now()

    @staticmethod
    async def accept_offer(db: AsyncSession, offer_id: int, user_id: int) -> ActiveOrderRead:
        async with db.begin():
            OfferedBook = aliased(Book)
            RequestedBook = aliased(Book)
            result = await db.execute(
                select(ExchangeOffer, OfferedBook, RequestedBook)
                .join(OfferedBook, OfferedBook.id == ExchangeOffer.offered_book_id)
                .join(RequestedBook, RequestedBook.id == ExchangeOffer.requested_book_id)
                .where(
                    ExchangeOffer.id == offer_id,
                    ExchangeOffer.status == "pending",
                    ExchangeOffer.expires_at > func.now(),
                    ExchangeOffer.to_user_id == user_id
                )
                .with_for_update()
            )

            row = result.one_or_none()
            if row is None:
                raise HTTPException(404, "Offer not found")

            db_offer, db_offered_book, db_requested_book = row
            if db_offered_book.status != "available":
                raise HTTPException(400, "Offered book not available")

            if db_requested_book.status != "available":
                raise HTTPException(400, "Requested book not available")

            db_offered_book.status = "reserved"
            db_requested_book.status = "reserved"

            db_offer.status = "accepted"
            db_offer.responded_at = func.now()

            # тут должно быть создание активного заказа

            #

        return ActiveOrderRead.model_validate()