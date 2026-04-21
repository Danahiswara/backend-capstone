import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "FastAPI App")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "False") == "True"

    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")
    SUPABASE_BUCKET: str = os.getenv("SUPABASE_BUCKET")

    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60)
    )

    AI_SERVICE_URL: str = os.getenv("AI_SERVICE_URL")
    USE_MOCK_AI: bool = os.getenv("USE_MOCK_AI")

settings = Settings()
