from src.models.models import Book, ExchangeOffer, User
from src.services.exchange_offers import ExchangeOfferService
import pytest
from fastapi import HTTPException
from src.schemas.exchange_offers import ExchangeOfferCreate
from datetime import datetime, timezone, timedelta


class TestGetUserOffers:
    async def test_get_all_user_offers(self, db_session, test_user_first, test_user_second, test_category):
        book1 = Book(
            title="Book1",
            author="A",
            description="D",
            thumbnail="t",
            category_id=test_category.id,
            owner_id=test_user_first.id,
        )
        book2 = Book(
            title="Book2",
            author="A",
            description="D",
            thumbnail="t",
            category_id=test_category.id,
            owner_id=test_user_second.id,
        )
        db_session.add_all([book1, book2])
        await db_session.flush()

        offer = ExchangeOffer(
            from_user_id=test_user_first.id,
            to_user_id=test_user_second.id,
            offered_book_id=book1.id,
            requested_book_id=book2.id,
        )
        db_session.add(offer)
        await db_session.flush()

        result = await ExchangeOfferService.get_user_offers(
            db_session,
            test_user_first.id,
            limit=10,
            offset=0,
        )

        assert len(result) == 1
        assert result[0].id == offer.id

    async def test_filter_incoming(self, db_session, test_user_first, test_user_second, test_category):
        book1 = Book(
            title="B1", author="A", description="D", thumbnail="t",
            category_id=test_category.id, owner_id=test_user_first.id
        )
        book2 = Book(
            title="B2", author="A", description="D", thumbnail="t",
            category_id=test_category.id, owner_id=test_user_second.id
        )
        db_session.add_all([book1, book2])
        await db_session.flush()

        incoming = ExchangeOffer(
            from_user_id=test_user_second.id,
            to_user_id=test_user_first.id,
            offered_book_id=book2.id,
            requested_book_id=book1.id,
        )
        outgoing = ExchangeOffer(
            from_user_id=test_user_first.id,
            to_user_id=test_user_second.id,
            offered_book_id=book1.id,
            requested_book_id=book2.id,
        )
        db_session.add_all([incoming, outgoing])
        await db_session.flush()

        result = await ExchangeOfferService.get_user_offers(
            db_session,
            test_user_first.id,
            limit=10,
            offset=0,
            direction="incoming"
        )

        assert len(result) == 1
        assert result[0].id == incoming.id

    async def test_filter_outgoing(self, db_session, test_user_first, test_user_second, test_category):
        book1 = Book(
            title="B1", author="A", description="D", thumbnail="t",
            category_id=test_category.id, owner_id=test_user_first.id
        )
        book2 = Book(
            title="B2", author="A", description="D", thumbnail="t",
            category_id=test_category.id, owner_id=test_user_second.id
        )
        db_session.add_all([book1, book2])
        await db_session.flush()

        offer = ExchangeOffer(
            from_user_id=test_user_first.id,
            to_user_id=test_user_second.id,
            offered_book_id=book1.id,
            requested_book_id=book2.id,
        )
        db_session.add(offer)
        await db_session.flush()

        result = await ExchangeOfferService.get_user_offers(
            db_session,
            test_user_first.id,
            limit=10,
            offset=0,
            direction="outgoing"
        )

        assert len(result) == 1
        assert result[0].id == offer.id

    async def test_filter_status(self, db_session, test_user_first, test_user_second, test_category):
        book1 = Book(
            title="B1", author="A", description="D", thumbnail="t",
            category_id=test_category.id, owner_id=test_user_first.id
        )
        book2 = Book(
            title="B2", author="A", description="D", thumbnail="t",
            category_id=test_category.id, owner_id=test_user_second.id
        )
        db_session.add_all([book1, book2])
        await db_session.flush()

        offer = ExchangeOffer(
            from_user_id=test_user_first.id,
            to_user_id=test_user_second.id,
            offered_book_id=book1.id,
            requested_book_id=book2.id,
            status="accepted"
        )
        db_session.add(offer)
        await db_session.flush()

        result = await ExchangeOfferService.get_user_offers(
            db_session,
            test_user_first.id,
            limit=10,
            offset=0,
            status="accepted"
        )

        assert len(result) == 1

    async def test_pagination(self, db_session, test_user_first, test_user_second, test_category):
        books = []
        for i in range(3):
            b = Book(
                title=f"B{i}", author="A", description="D", thumbnail="t",
                category_id=test_category.id, owner_id=test_user_first.id
            )
            books.append(b)
        db_session.add_all(books)
        await db_session.flush()

        for i in range(3):
            offer = ExchangeOffer(
                from_user_id=test_user_first.id,
                to_user_id=test_user_second.id,
                offered_book_id=books[i].id,
                requested_book_id=books[i].id,
            )
            db_session.add(offer)
        await db_session.flush()

        result = await ExchangeOfferService.get_user_offers(
            db_session,
            test_user_first.id,
            limit=2,
            offset=0,
        )

        assert len(result) == 2

    async def test_empty(self, db_session, test_user_first):
        result = await ExchangeOfferService.get_user_offers(
            db_session,
            test_user_first.id,
            limit=10,
            offset=0,
        )
        assert result == []


class TestGetOneOffer:
    async def test_success_owner(self, db_session, test_user_first, test_user_second, test_category):
        book1 = Book(
            title="B1", author="A", description="D", thumbnail="t",
            category_id=test_category.id, owner_id=test_user_first.id
        )
        book2 = Book(
            title="B2", author="A", description="D", thumbnail="t",
            category_id=test_category.id, owner_id=test_user_second.id
        )
        db_session.add_all([book1, book2])
        await db_session.flush()

        offer = ExchangeOffer(
            from_user_id=test_user_first.id,
            to_user_id=test_user_second.id,
            offered_book_id=book1.id,
            requested_book_id=book2.id,
        )
        db_session.add(offer)
        await db_session.flush()

        result = await ExchangeOfferService.get_one_offer(
            db_session,
            test_user_first.id,
            offer.id
        )

        assert result.id == offer.id

    async def test_success_receiver(self, db_session, test_user_first, test_user_second, test_category):
        book1 = Book(
            title="B1", author="A", description="D", thumbnail="t",
            category_id=test_category.id, owner_id=test_user_first.id
        )
        book2 = Book(
            title="B2", author="A", description="D", thumbnail="t",
            category_id=test_category.id, owner_id=test_user_second.id
        )
        db_session.add_all([book1, book2])
        await db_session.flush()

        offer = ExchangeOffer(
            from_user_id=test_user_first.id,
            to_user_id=test_user_second.id,
            offered_book_id=book1.id,
            requested_book_id=book2.id,
        )
        db_session.add(offer)
        await db_session.flush()

        result = await ExchangeOfferService.get_one_offer(
            db_session,
            test_user_second.id,
            offer.id
        )

        assert result.id == offer.id

    async def test_not_participant(self, db_session, test_user_first, test_user_second, test_category):
        user3 = User(
            username="u3",
            email="u3@mail.com",
            password="12345678",
            full_name="u3"
        )
        db_session.add(user3)
        await db_session.flush()

        book1 = Book(
            title="B1", author="A", description="D", thumbnail="t",
            category_id=test_category.id, owner_id=test_user_first.id
        )
        book2 = Book(
            title="B2", author="A", description="D", thumbnail="t",
            category_id=test_category.id, owner_id=test_user_second.id
        )
        db_session.add_all([book1, book2])
        await db_session.flush()

        offer = ExchangeOffer(
            from_user_id=test_user_first.id,
            to_user_id=test_user_second.id,
            offered_book_id=book1.id,
            requested_book_id=book2.id,
        )
        db_session.add(offer)
        await db_session.flush()

        with pytest.raises(HTTPException):
            await ExchangeOfferService.get_one_offer(
                db_session,
                user3.id,
                offer.id
            )

    async def test_not_found(self, db_session, test_user_first):
        with pytest.raises(HTTPException) as exc:
            await ExchangeOfferService.get_one_offer(
                db_session,
                test_user_first.id,
                999
            )

        assert exc.value.status_code == 404


class TestCreateOffer:
    async def test_success(self, db_session, test_user_first, test_user_second, test_category):
        book1 = Book(
            title="B1", author="A", description="D", thumbnail="t",
            category_id=test_category.id,
            owner_id=test_user_first.id,
            status="available"
        )
        book2 = Book(
            title="B2", author="A", description="D", thumbnail="t",
            category_id=test_category.id,
            owner_id=test_user_second.id,
            status="available"
        )
        db_session.add_all([book1, book2])
        await db_session.flush()

        data = ExchangeOfferCreate(
            from_user_id=test_user_first.id,
            to_user_id=test_user_second.id,
            offered_book_id=book1.id,
            requested_book_id=book2.id
        )

        result = await ExchangeOfferService.create_offer(
            db_session,
            test_user_first.id,
            data
        )

        assert result.id is not None
        assert result.from_user_id == test_user_first.id

    async def test_permission_denied(self, db_session, test_user_first, test_user_second, test_category):
        data = ExchangeOfferCreate(
            from_user_id=test_user_first.id,
            to_user_id=test_user_second.id,
            offered_book_id=1,
            requested_book_id=2
        )

        with pytest.raises(HTTPException) as exc:
            await ExchangeOfferService.create_offer(
                db_session,
                user_id=test_user_second.id,
                data=data
            )

        assert exc.value.status_code == 403

    async def test_same_user(self, db_session, test_user_first):
        data = ExchangeOfferCreate(
            from_user_id=test_user_first.id,
            to_user_id=test_user_first.id,
            offered_book_id=1,
            requested_book_id=2
        )

        with pytest.raises(HTTPException) as exc:
            await ExchangeOfferService.create_offer(
                db_session,
                test_user_first.id,
                data
            )

        assert exc.value.status_code == 400

    async def test_same_books(self, db_session, test_user_first, test_user_second):
        data = ExchangeOfferCreate(
            from_user_id=test_user_first.id,
            to_user_id=test_user_second.id,
            offered_book_id=1,
            requested_book_id=1
        )

        with pytest.raises(HTTPException) as exc:
            await ExchangeOfferService.create_offer(
                db_session,
                test_user_first.id,
                data
            )

        assert exc.value.status_code == 400

    async def test_books_not_found(self, db_session, test_user_first, test_user_second):
        data = ExchangeOfferCreate(
            from_user_id=test_user_first.id,
            to_user_id=test_user_second.id,
            offered_book_id=999,
            requested_book_id=888
        )

        with pytest.raises(HTTPException) as exc:
            await ExchangeOfferService.create_offer(
                db_session,
                test_user_first.id,
                data
            )

        assert exc.value.status_code == 404

    async def test_offered_book_not_owned(self, db_session, test_user_first, test_user_second, test_category):
        book = Book(
            title="B1", author="A", description="D", thumbnail="t",
            category_id=test_category.id,
            owner_id=test_user_second.id,
            status="available"
        )
        db_session.add(book)
        await db_session.flush()

        data = ExchangeOfferCreate(
            from_user_id=test_user_first.id,
            to_user_id=test_user_second.id,
            offered_book_id=book.id,
            requested_book_id=book.id
        )

        with pytest.raises(HTTPException):
            await ExchangeOfferService.create_offer(
                db_session,
                test_user_first.id,
                data
            )

    async def test_requested_book_not_owned(self, db_session, test_user_first, test_user_second, test_category):
        book1 = Book(
            title="B1", author="A", description="D", thumbnail="t",
            category_id=test_category.id,
            owner_id=test_user_first.id,
            status="available"
        )
        book2 = Book(
            title="B2", author="A", description="D", thumbnail="t",
            category_id=test_category.id,
            owner_id=test_user_first.id,
            status="available"
        )
        db_session.add_all([book1, book2])
        await db_session.flush()

        data = ExchangeOfferCreate(
            from_user_id=test_user_first.id,
            to_user_id=test_user_second.id,
            offered_book_id=book1.id,
            requested_book_id=book2.id
        )

        with pytest.raises(HTTPException):
            await ExchangeOfferService.create_offer(
                db_session,
                test_user_first.id,
                data
            )

    async def test_book_not_available(self, db_session, test_user_first, test_user_second, test_category):
        book1 = Book(
            title="B1", author="A", description="D", thumbnail="t",
            category_id=test_category.id,
            owner_id=test_user_first.id,
            status="reserved"
        )
        book2 = Book(
            title="B2", author="A", description="D", thumbnail="t",
            category_id=test_category.id,
            owner_id=test_user_second.id,
            status="available"
        )
        db_session.add_all([book1, book2])
        await db_session.flush()

        data = ExchangeOfferCreate(
            from_user_id=test_user_first.id,
            to_user_id=test_user_second.id,
            offered_book_id=book1.id,
            requested_book_id=book2.id
        )

        with pytest.raises(HTTPException):
            await ExchangeOfferService.create_offer(
                db_session,
                test_user_first.id,
                data
            )


class TestDeclineOffer:
    async def test_success_by_sender(self, db_session, test_user_first, test_user_second, test_category):
        book1 = Book(
            title="B1", author="A", description="D", thumbnail="t",
            category_id=test_category.id,
            owner_id=test_user_first.id,
            status="available"
        )
        book2 = Book(
            title="B2", author="A", description="D", thumbnail="t",
            category_id=test_category.id,
            owner_id=test_user_second.id,
            status="available"
        )
        db_session.add_all([book1, book2])
        await db_session.flush()

        offer = ExchangeOffer(
            from_user_id=test_user_first.id,
            to_user_id=test_user_second.id,
            offered_book_id=book1.id,
            requested_book_id=book2.id,
        )
        db_session.add(offer)
        await db_session.flush()

        await ExchangeOfferService.decline_offer(
            db_session,
            offer.id,
            test_user_first.id
        )

        assert offer.status == "declined"

    async def test_success_by_receiver(self, db_session, test_user_first, test_user_second, test_category):
        book1 = Book(
            title="B1", author="A", description="D", thumbnail="t",
            category_id=test_category.id,
            owner_id=test_user_first.id,
            status="available"
        )
        book2 = Book(
            title="B2", author="A", description="D", thumbnail="t",
            category_id=test_category.id,
            owner_id=test_user_second.id,
            status="available"
        )
        db_session.add_all([book1, book2])
        await db_session.flush()

        offer = ExchangeOffer(
            from_user_id=test_user_first.id,
            to_user_id=test_user_second.id,
            offered_book_id=book1.id,
            requested_book_id=book2.id,
        )
        db_session.add(offer)
        await db_session.flush()

        await ExchangeOfferService.decline_offer(
            db_session,
            offer.id,
            test_user_second.id
        )

        assert offer.status == "declined"

    async def test_not_participant(self, db_session, test_user_first, test_user_second, test_category):
        user3 = User(
            username="u3",
            email="u3@mail.com",
            password="12345678",
            full_name="u3"
        )
        db_session.add(user3)
        await db_session.flush()

        book1 = Book(
            title="B1", author="A", description="D", thumbnail="t",
            category_id=test_category.id,
            owner_id=test_user_first.id,
            status="available"
        )
        book2 = Book(
            title="B2", author="A", description="D", thumbnail="t",
            category_id=test_category.id,
            owner_id=test_user_second.id,
            status="available"
        )
        db_session.add_all([book1, book2])
        await db_session.flush()

        offer = ExchangeOffer(
            from_user_id=test_user_first.id,
            to_user_id=test_user_second.id,
            offered_book_id=book1.id,
            requested_book_id=book2.id,
        )
        db_session.add(offer)
        await db_session.flush()

        with pytest.raises(HTTPException):
            await ExchangeOfferService.decline_offer(
                db_session,
                offer.id,
                user3.id
            )

    async def test_not_found(self, db_session, test_user_first):
        with pytest.raises(HTTPException) as exc:
            await ExchangeOfferService.decline_offer(
                db_session,
                999,
                test_user_first.id
            )

        assert exc.value.status_code == 404

    async def test_already_not_pending(self, db_session, test_user_first, test_user_second, test_category):
        book1 = Book(
            title="B1", author="A", description="D", thumbnail="t",
            category_id=test_category.id,
            owner_id=test_user_first.id,
            status="available"
        )
        book2 = Book(
            title="B2", author="A", description="D", thumbnail="t",
            category_id=test_category.id,
            owner_id=test_user_second.id,
            status="available"
        )
        db_session.add_all([book1, book2])
        await db_session.flush()

        offer = ExchangeOffer(
            from_user_id=test_user_first.id,
            to_user_id=test_user_second.id,
            offered_book_id=book1.id,
            requested_book_id=book2.id,
            status="accepted"
        )
        db_session.add(offer)
        await db_session.flush()

        with pytest.raises(HTTPException):
            await ExchangeOfferService.decline_offer(
                db_session,
                offer.id,
                test_user_first.id
            )

    async def test_expired_offer(self, db_session, test_user_first, test_user_second, test_category):
        book1 = Book(
            title="B1", author="A", description="D", thumbnail="t",
            category_id=test_category.id,
            owner_id=test_user_first.id,
            status="available"
        )
        book2 = Book(
            title="B2", author="A", description="D", thumbnail="t",
            category_id=test_category.id,
            owner_id=test_user_second.id,
            status="available"
        )
        db_session.add_all([book1, book2])
        await db_session.flush()

        offer = ExchangeOffer(
            from_user_id=test_user_first.id,
            to_user_id=test_user_second.id,
            offered_book_id=book1.id,
            requested_book_id=book2.id,
            expires_at=datetime.now(timezone.utc) - timedelta(days=1)
        )
        db_session.add(offer)
        await db_session.flush()

        with pytest.raises(HTTPException):
            await ExchangeOfferService.decline_offer(
                db_session,
                offer.id,
                test_user_first.id
            )


class TestAcceptOffer:
    async def test_success(self, db_session, offer_factory, book_factory, user_factory):
        user1 = await user_factory()
        user2 = await user_factory()

        book1 = await book_factory(owner_id=user1.id, status="available")
        book2 = await book_factory(owner_id=user2.id, status="available")

        offer = await offer_factory(
            from_user_id=user1.id,
            to_user_id=user2.id,
            offered_book_id=book1.id,
            requested_book_id=book2.id,
            status="pending",
        )

        result = await ExchangeOfferService.accept_offer(db_session, offer.id, user2.id)

        assert result is not None
        assert offer.status == "accepted"
        assert book1.status == "reserved"
        assert book2.status == "reserved"

    async def test_not_found(self, db_session):
        with pytest.raises(HTTPException):
            await ExchangeOfferService.accept_offer(db_session, 999, 1)

    async def test_wrong_user(self, db_session, offer_factory):
        offer = await offer_factory(status="pending")
        with pytest.raises(HTTPException):
            await ExchangeOfferService.accept_offer(db_session, offer.id, 999)

    async def test_offered_book_not_available(self, db_session, offer_factory, book_factory, user_factory):
        user1 = await user_factory()
        user2 = await user_factory()

        book1 = await book_factory(owner_id=user1.id, status="reserved")
        book2 = await book_factory(owner_id=user2.id, status="available")

        offer = await offer_factory(
            from_user_id=user1.id,
            to_user_id=user2.id,
            offered_book_id=book1.id,
            requested_book_id=book2.id,
            status="pending",
        )

        with pytest.raises(HTTPException):
            await ExchangeOfferService.accept_offer(db_session, offer.id, user2.id)

    async def test_requested_book_not_available(self, db_session, offer_factory, book_factory, user_factory):
        user1 = await user_factory()
        user2 = await user_factory()

        book1 = await book_factory(owner_id=user1.id, status="available")
        book2 = await book_factory(owner_id=user2.id, status="reserved")

        offer = await offer_factory(
            from_user_id=user1.id,
            to_user_id=user2.id,
            offered_book_id=book1.id,
            requested_book_id=book2.id,
            status="pending",
        )

        with pytest.raises(HTTPException):
            await ExchangeOfferService.accept_offer(db_session, offer.id, user2.id)




