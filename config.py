import os

# 数据库配置
DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///./../chatstar_data.db')

# JWT 认证配置
SECRET_KEY: str = os.getenv('SECRET_KEY', 'default-secret-key')
ALGORITHM: str = 'HS256'
ACCESS_TOKEN_EXPIRE_DAYS: int = 7

# 应用配置
APP_TITLE: str = 'ChatStar管理后台'
APP_HOST: str = os.getenv('APP_HOST', '0.0.0.0')
APP_PORT: int = int(os.getenv('APP_PORT', '8000'))

# AWS S3
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
AWS_REGION = os.environ.get("AWS_REGION", "")
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "")