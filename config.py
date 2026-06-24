from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    DATABASE_URL: str = "sqlite:///./chatstar_admin.db"
    
    class Config:
        env_file = ".env"

settings = Settings()
