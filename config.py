import os
from dotenv import load_dotenv

load_dotenv()

def get_env(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise Exception(f"环境变量 {key} 未配置！")
    return val

ENV_MODE = get_env("ENV_MODE")

if ENV_MODE == "develop":
    print("本地开发环境")
elif ENV_MODE == "production":
    print("线上生产环境")

# 数据库配置
DATABASE_URL: str = get_env('DATABASE_URL')

# JWT 认证配置
SECRET_KEY: str = get_env('SECRET_KEY')
ALGORITHM: str = 'HS256'
ACCESS_TOKEN_EXPIRE_DAYS: int = 7

# 应用配置
APP_TITLE: str = 'ChatStar管理后台'
APP_HOST: str = os.getenv('APP_HOST', '0.0.0.0')
APP_PORT: int = int(os.getenv('APP_PORT', '8000'))

# Cloudflare R2
R2_ACCESS_KEY = get_env('R2_ACCESS_KEY')
R2_SECRET_KEY = get_env('R2_SECRET_KEY')
R2_ACCOUNT_ID = get_env('R2_ACCOUNT_ID')
R2_BUCKET_NAME = get_env('R2_BUCKET_NAME')
R2_ENDPOINT = get_env('R2_ENDPOINT')
R2_DEV_PUB_URL = get_env('R2_DEV_PUB_URL')
WORKER_API_URL = get_env('WORKER_API_URL')