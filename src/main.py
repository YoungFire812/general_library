from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

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
from loguru import logger
import sys

from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from src.core.limiter import limiter


logger.remove()
logger.add(
    sys.stdout,
    level=settings.LOG_LEVEL,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)

if settings.MODE == "PROD":
    logger.add(
        "logs/app.log",
        rotation="500 MB",
        retention="30 days",
        compression="zip",
        level="ERROR",
        serialize=True,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_minio_bucket()
    await asyncio.to_thread(make_bucket_public)

    await init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter

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