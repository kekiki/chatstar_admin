import os
import boto3
import uuid
from botocore.config import Config
from config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, S3_BUCKET_NAME

class AWSS3Client:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION,
            config=Config(signature_version='s3v4')
        )
        self.bucket_name = S3_BUCKET_NAME

    def get_unique_key(self, origin_name: str, prefix: str) -> str:
        """生成唯一文件路径，防止覆盖"""
        if "." in origin_name:
            ext = origin_name.split(".")[-1]
            return f"{prefix}/{uuid.uuid4()}.{ext}"
        return f"{prefix}/{uuid.uuid4()}"

    def upload_and_get_link(self, file_bytes: bytes, file_name: str, file_content_type: str = 'image') -> dict:
        """上传文件并返回下载链接"""
        key = self.get_unique_key(file_name, file_content_type)
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=file_bytes,
            ContentType=file_content_type,
            ACL="public-read"
        )
        return {
            "key": key,
            "url": f"https://{self.bucket_name}.s3.{AWS_REGION}.amazonaws.com/{key}"
        }
        