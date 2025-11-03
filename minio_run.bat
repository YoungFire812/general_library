@echo off
docker run -d -p 9000:9000 -p 9001:9001 -e MINIO_ROOT_USER=admin -e MINIO_ROOT_PASSWORD=admin123 -e MINIO_BROWSER=on -v minio_data:/data --name minio minio/minio server /data --console-address ":9001"
exit
