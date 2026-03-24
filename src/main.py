import asyncio
import sys
from contextlib import asynccontextmanager
from loguru import logger
from slowapi.errors import RateLimitExceeded

from fastapi import FastAPI, APIRouter, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.core.config import settings
from src.routers.files import files_router
from src.routers.books import books_router
from src.routers.categories import categories_router
from src.routers.carts import carts_router
from src.routers.users import users_router
from src.routers.exchange_offers import exchange_offers_router
from src.routers.lockers import lockers_router
from src.routers.active_orders import active_orders_router
from src.routers.auth import auth_router
from src.minio.minio_client import init_minio_bucket, make_bucket_public
from src.db.database import init_db
from src.core.limiter import limiter
from src.core.exceptions import http_exception_handler, general_exception_handler
from src.middleware.request_id import request_id_middleware
from src.middleware.logging import logging_middleware
from src.core.logger import setup_logger


setup_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_minio_bucket()
    await asyncio.to_thread(make_bucket_public)

    await init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter

app.middleware("http")(request_id_middleware)
app.middleware("http")(logging_middleware)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(books_router)
v1_router.include_router(files_router)
v1_router.include_router(categories_router)
v1_router.include_router(carts_router)
v1_router.include_router(users_router)
v1_router.include_router(exchange_offers_router)
v1_router.include_router(lockers_router)
v1_router.include_router(active_orders_router)

app.include_router(v1_router)
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests"}
    )