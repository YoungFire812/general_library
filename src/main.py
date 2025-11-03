import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from src.auth.config import AuthConfig
from src.config import Config
from src.routers.files import files_router
from src.routers.books import books_router
from src.routers.categories import categories_router
from src.minio.minio_client import init_minio_bucket, make_bucket_public
from src.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_minio_bucket()
    await asyncio.to_thread(make_bucket_public)

    await init_db()
    yield


app = FastAPI(lifespan=lifespan)

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(books_router)
v1_router.include_router(files_router)
v1_router.include_router(categories_router)

app.include_router(v1_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # адрес Vite dev сервера
    allow_methods=["*"],
    allow_headers=["*"],
)




