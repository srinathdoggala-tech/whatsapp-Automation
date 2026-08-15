from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    DATABASE_URL: str = "sqlite+aiosqlite:///:memory:"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "dev-secret-key"
    
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"
    
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "meta-llama/llama-3.1-70b-instruct"
    OPENROUTER_API_URL: str = "https://openrouter.ai/api/v1/chat/completions"
    
    LLM_PROVIDER: str = "mock"
    
    WHATSAPP_ACCESS_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_BUSINESS_ACCOUNT_ID: str = ""
    WHATSAPP_VERIFY_TOKEN: str = ""
    WHATSAPP_APP_SECRET: str = ""
    
    NEXT_PUBLIC_API_URL: str = "http://localhost:8000/api"
    
    MIN_RESPONSE_DELAY: int = 3
    MAX_RESPONSE_DELAY: int = 18
    BURST_WINDOW_MS: int = 5000
    CONFIDENCE_THRESHOLD: float = 0.7
    MAX_AUTO_REPLY_LENGTH: int = 500

settings = Settings()
