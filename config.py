from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # MongoDB connection URL, can be set via environment variable MONGODB_URL
    mongodb_url: str = os.getenv("MONGO_URL", "mongodb+srv://manishtravhoo_db_user:S5NnimoeXGz24nxU@travhoo-web.agcc3gy.mongodb.net/?retryWrites=true&w=majority&appName=travhoo-web")
    # Database name, can be set via environment variable DATABASE_NAME
    database_name: str = os.getenv("DB_NAME", "travhoo")
    # Secret key for cryptographic operations (e.g., signing session data).
    # This should be a long, random string and kept secret.
    # Set it via environment variable SECRET_KEY for security.
    secret_key: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-this-in-production-12345")
    # Algorithm for cryptographic operations, can be set via ALGORITHM env var
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    # Session expiration in minutes, can be set via ACCESS_TOKEN_EXPIRE_MINUTES env var
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra environment variables

settings = Settings()
