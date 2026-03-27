import pytest
from alembic.util import status
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.pool import NullPool

from src.models.models import *
from src.core.security import hash_password
from datetime import datetime, timezone, timedelta
import random


TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5433/test_db"


@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture
async def connection(engine):
    async with engine.connect() as conn:
        tx = await conn.begin()
        yield conn
        await tx.rollback()


@pytest.fixture
async def db_session(connection):
    session_maker = async_sessionmaker(
        bind=connection,
        expire_on_commit=False,
        class_=AsyncSession
    )

    async with session_maker() as session:
        yield session

@pytest.fixture
async def test_user_first(db_session):
    user = User(
        username="Vasili",
        email="vasili@mail.ru",
        password=await hash_password("vasilikrutoi"),
        full_name="Vasili Ivanov",
    )
    db_session.add(user)
    await db_session.flush()
    return user

@pytest.fixture
async def test_user_second(db_session):
    user = User(
        username="Dima338",
        email="dima@mail.ru",
        password=await hash_password("dima1111111"),
        full_name="Dima Ivanov",
    )
    db_session.add(user)
    await db_session.flush()
    return user

@pytest.fixture
async def test_category(db_session):
    category = Category(
        id=1,
        name="Test Category"
    )
    db_session.add(category)
    await db_session.flush()
    return category

@pytest.fixture
async def another_category(db_session):
    category = Category(
        id=2,
        name="Another Test Category"
    )
    db_session.add(category)
    await db_session.flush()
    return category


@pytest.fixture
async def offer_factory(db_session, user_factory, book_factory, test_category):
    async def create_offer(**kwargs):
        from_user = kwargs.get("from_user") or await user_factory()
        to_user = kwargs.get("to_user") or await user_factory()

        offered_book = kwargs.get("offered_book") or await book_factory(owner_id=from_user.id,
                                                                        category_id=test_category.id)
        requested_book = kwargs.get("requested_book") or await book_factory(owner_id=to_user.id,
                                                                            category_id=test_category.id)

        offer = ExchangeOffer(
            from_user_id=kwargs.get("from_user_id", from_user.id),
            to_user_id=kwargs.get("to_user_id", to_user.id),
            offered_book_id=kwargs.get("offered_book_id", offered_book.id),
            requested_book_id=kwargs.get("requested_book_id", requested_book.id),
            status=kwargs.get("status", "pending"),
            expires_at=kwargs.get("expires_at", datetime.now(timezone.utc) + timedelta(days=1)),
        )
        db_session.add(offer)
        await db_session.flush()
        await db_session.refresh(offer)
        return offer

    return create_offer

@pytest.fixture
async def book_factory(db_session, test_category):
    async def create_book(**kwargs):
        book = Book(
            title=kwargs.get("title", "Test Book"),
            author=kwargs.get("author", "Unknown Author"),
            description=kwargs.get("description", "No description"),
            thumbnail=kwargs.get("thumbnail", "default.png"),
            status=kwargs.get("status", "available"),
            owner_id=kwargs["owner_id"],
            category_id=kwargs.get("category_id", test_category.id),
            images=kwargs.get("images", []),
            is_published=kwargs.get("is_published", True),
        )
        db_session.add(book)
        await db_session.flush()
        await db_session.refresh(book)
        return book

    return create_book

@pytest.fixture
async def user_factory(db_session):
    counter = 0

    async def create_user(**kwargs):
        nonlocal counter
        counter += 1

        user = User(
            username=kwargs.get("username", f"user{counter}"),
            email=kwargs.get("email", f"user{counter}@mail.com"),
            password=await hash_password(kwargs.get("password", "password123")),
            full_name=kwargs.get("full_name", "Test User"),
            role=kwargs.get("role", "user"),
        )

        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)
        return user

    return create_user

@pytest.fixture
async def locker_factory(db_session):
    counter = 0

    async def _create_locker(name: str | None = None, address: str | None = None, available_slots: int | None = None):
        nonlocal counter
        counter += 1

        lat = 10.0 + counter * 0.001
        lng = 20.0 + counter * 0.001

        locker = Locker(
            name=name or f"Locker {counter}",
            address=address or f"Address {counter}",
            available_slots=available_slots if available_slots is not None else 1,
            lat=lat,
            lng=lng,
        )
        db_session.add(locker)
        await db_session.flush()
        await db_session.refresh(locker)
        return locker

    return _create_locker
