from fastapi import APIRouter, UploadFile, File
from src.minio.minio_client import upload_file_to_minio

from typing import List

files_router = APIRouter(prefix="/upload-files")


@files_router.post("", tags=["Files"])
async def upload_files(files: List[UploadFile] = File(...)):
    uploaded_links = []
    for file in files:
        link = await upload_file_to_minio(file)
        uploaded_links.append(link)

    return {"message": "Success file upload", "files": uploaded_links}
