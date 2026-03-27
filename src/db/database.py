from fastapi import HTTPException

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from src.db.base import Base
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from src.core.config import settings
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger
from sqlalchemy import text


DATABASE_URL = f"postgresql+asyncpg://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@{settings.DB_HOSTNAME}:{settings.DB_PORT}/{settings.DB_NAME}"
DEFAULT_DB_URL = f"postgresql+asyncpg://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@{settings.DB_HOSTNAME}:{settings.DB_PORT}/postgres"

engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
)


async def create_database_if_not_exists():
    from sqlalchemy.ext.asyncio import create_async_engine
    default_engine = create_async_engine(DEFAULT_DB_URL, isolation_level="AUTOCOMMIT")
    async with default_engine.begin() as conn:
        result = await conn.execute(
            text(f"SELECT 1 FROM pg_database WHERE datname='{settings.DB_NAME}'")
        )
        exists = result.scalar()
        if not exists:
            logger.info(f"Database {settings.DB_NAME} does not exist. Creating...")
            await conn.execute(text(f'CREATE DATABASE "{settings.DB_NAME}"'))
    await default_engine.dispose()

async def init_db():
    await create_database_if_not_exists()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


AsyncSessionLocal: sessionmaker[AsyncSession] = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()

        except HTTPException:
            await session.rollback()
            raise

        except SQLAlchemyError as e:
            await session.rollback()
            logger.bind(database=True, error_type=type(e).__name__).exception("Database error")
            raise

        except Exception as e:
            await session.rollback()
            logger.bind(database=True, critical=True, error_type=type(e).__name__).exception("Unexpected error in DB session")
            raise

        finally:
            await session.close()
