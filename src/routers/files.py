from fastapi import APIRouter, UploadFile, File
from typing import List
from loguru import logger
from src.minio.minio_client import upload_file_to_minio


files_router = APIRouter(prefix="/upload-files")


@files_router.post("", tags=["Files"])
async def upload_files(files: List[UploadFile] = File(...)):
    logger.info("Start file upload", files_count=len(files))

    uploaded_links = []

    for file in files:
        try:
            logger.debug("Uploading file", filename=file.filename)
            link = await upload_file_to_minio(file)
        except Exception:
            logger.exception("File upload failed", filename=file.filename)
            raise

        uploaded_links.append(link)

    logger.info("Files uploaded successfully", files_count=len(files))

    return {
        "message": "Success file upload",
        "files": uploaded_links
    }
