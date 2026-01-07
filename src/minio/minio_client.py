import asyncio
import json

from minio import Minio
from src.core.config import settings
from fastapi import UploadFile
from io import BytesIO
import uuid


def get_minio_client():
    return Minio(
        endpoint=settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ROOT_USER,
        secret_key=settings.MINIO_ROOT_PASSWORD,
        secure=settings.MINIO_SECURE
    )

async def init_minio_bucket():
    loop = asyncio.get_running_loop()
    client = get_minio_client()
    exists = await loop.run_in_executor(None, client.bucket_exists, settings.MINIO_BUCKET)
    if not exists:
        await loop.run_in_executor(None, client.make_bucket, settings.MINIO_BUCKET)

def make_bucket_public():
    client = get_minio_client()
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": "*",
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{settings.MINIO_BUCKET}/*"]
            }
        ]
    }
    client.set_bucket_policy(settings.MINIO_BUCKET, json.dumps(policy))


async def upload_file_to_minio(file: UploadFile):
    loop = asyncio.get_running_loop()
    client = get_minio_client()
    content = await file.read()
    file_stream = BytesIO(content)
    unique_filename = f"{uuid.uuid4().hex}_{file.filename}"

    await loop.run_in_executor(
        None,
        client.put_object,
        settings.MINIO_BUCKET,
        unique_filename,
        file_stream,
        len(content)
    )

    return f"http://localhost:{settings.MINIO_ENDPOINT.split(':')[-1]}/{settings.MINIO_BUCKET}/{unique_filename}"


