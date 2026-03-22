from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from src.db.base import Base
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from src.core.config import settings
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from loguru import logger
from src.core.sqlErrors import UNIQUE_VIOLATION, NOT_NULL_VIOLATION, is_error
from sqlalchemy.exc import IntegrityError


DATABASE_URL = f"postgresql+asyncpg://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@{settings.DB_HOSTNAME}:{settings.DB_PORT}/{settings.DB_NAME}"

engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
)


async def init_db():
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

        except IntegrityError as e:
            await session.rollback()
            if await is_error(e, UNIQUE_VIOLATION):
                raise HTTPException(status_code=409, detail="object with this data is already exists")
            elif await is_error(e, NOT_NULL_VIOLATION):
                raise HTTPException(status_code=409, detail="some data cannot be None")
            else:
                raise HTTPException(status_code=500, detail="Internal Database Error")
        except SQLAlchemyError:
            await session.rollback()
            logger.bind(database=True).exception(
                "Критическая ошибка при работе с БД в транзакции"
            )
            raise HTTPException(status_code=500, detail="Internal Database Error")
        except HTTPException:
            await session.rollback()
            raise
        except Exception as e:
            await session.rollback()
            logger.bind(critical=True).exception(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="Unexpected server error")
        finally:
            await session.close()
