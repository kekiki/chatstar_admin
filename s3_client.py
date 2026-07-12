import os
import uuid
import requests
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from config import R2_ACCESS_KEY, R2_SECRET_KEY, R2_ACCOUNT_ID, R2_BUCKET_NAME, R2_ENDPOINT, WORKER_API_URL, R2_DEV_PUB_URL
import httpx
from fastapi import HTTPException

class AWSS3Client:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=R2_ACCESS_KEY,
            aws_secret_access_key=R2_SECRET_KEY,
            endpoint_url=R2_ENDPOINT,
            region_name='auto',
            config=Config(signature_version='s3v4')
        )
        self.account_id = R2_ACCOUNT_ID
        self.end_point = R2_ENDPOINT
        self.bucket_name = R2_BUCKET_NAME

    async def get_r2_upload_url(self, file_name: str, content_type: str):
        # 请求到Workers生成预签名直链
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                WORKER_API_URL,
                headers = {
                    "Content-Type": "applcation/json",
                },
                json={
                    "fileName": file_name,
                    "contentType": content_type
                },
                timeout=10
            )
            print(resp.json())
            if resp.status_code != 200:
                raise HTTPException(status_code=500, detail="获取R2上传直链失败")

        return resp.json()

    # 后端PUT上传示例
    async def upload_bytes(self, file_bytes: str, object_key: str):
        try:
            self.s3_client.put_object(
                Bucket=R2_BUCKET_NAME,
                Key=object_key,
                Body=file_bytes
            )
            file_url = f"{R2_DEV_PUB_URL}/{object_key}"
            return file_url
        except Exception as e:
            raise HTTPException(500, f"R2上传失败: {str(e)}")
    
    # 删除桶内文件
    def delete_file(self, object_key: str):
        self.s3_client.delete_object(Bucket=self.bucket_name, Key=object_key)
    
    # 判断文件是否存在
    def file_exists(self, object_key: str) -> bool:
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=object_key)
            return True
        except ClientError:
            return False

    def get_unique_key(self, origin_name: str) -> str:
        """生成唯一文件路径，防止覆盖"""
        if "." in origin_name:
            ext = origin_name.split(".")[-1]
            return f"{uuid.uuid4()}.{ext}"
        return f"{uuid.uuid4()}"

    async def upload_and_get_link(self, file_bytes: bytes, file_name: str, file_content_type: str) -> dict:
        """上传文件并返回下载链接"""
        # data = await self.get_r2_upload_url(self.get_unique_key(file_name), file_content_type)
        # print('get_r2_upload_url:')
        # print(data)
        # upload_url = data.get("uploadUrl")
        # public_url = data.get("publicUrl")
        # if not upload_url or not public_url:
        #     raise RuntimeError("Worker 返回数据缺失 uploadUrl/publicUrl")

        object_key = f'uploads/{self.get_unique_key(file_name)}'
        public_url = await self.upload_bytes(file_bytes, object_key)
        return {
            "url": public_url
        }
        