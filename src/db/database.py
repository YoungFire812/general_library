from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from src.db.base import Base
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from src.core.config import settings
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger


DATABASE_URL = f"postgresql+asyncpg://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@{settings.DB_HOSTNAME}:{settings.DB_PORT}/{settings.DB_NAME}"

engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
)

logger.info("db_init_start")

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

logger.info("db_init_success")

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
