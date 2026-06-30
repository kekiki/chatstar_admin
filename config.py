import os
from typing import Optional

# 数据库配置
DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///./chatstar_data.db')

# JWT 认证配置
SECRET_KEY: str = os.getenv('SECRET_KEY', 'default-secret-key')
ALGORITHM: str = 'HS256'
ACCESS_TOKEN_EXPIRE_DAYS: int = 7

# 应用配置
APP_TITLE: str = 'ChatStar管理后台'
APP_HOST: str = os.getenv('APP_HOST', '0.0.0.0')
APP_PORT: int = int(os.getenv('APP_PORT', '8000'))

# Zoho OAuth
ZOHO_CLIENT_ID = os.environ.get("ZOHO_CLIENT_ID", "")
ZOHO_CLIENT_SECRET = os.environ.get("ZOHO_CLIENT_SECRET", "")
ZOHO_REFRESH_TOKEN = os.environ.get("ZOHO_REFRESH_TOKEN", "")
ZOHO_ACCOUNT_URL = os.environ.get("ZOHO_ACCOUNT_URL", "")
ZOHO_ORG_ID = os.environ.get("ZOHO_ORG_ID", "")
ZOHO_ROOT_FOLDER_ID = os.environ.get("ZOHO_ROOT_FOLDER_ID", "")

# AWS S3
# AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "")
# AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
# AWS_REGION = os.environ.get("AWS_REGION", "")
# S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "")
AWS_ACCESS_KEY_ID="AKIAW5PEW3QDNCLM6PPB"
AWS_SECRET_ACCESS_KEY="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"
AWS_REGION="ap-southeast-1"
S3_BUCKET_NAME="chatstar-475610405894-ap-southeast-1-an"