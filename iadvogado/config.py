from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    fastapi_host: str = "0.0.0.0"
    fastapi_port: int = 8000
    supabase_url: str
    supabase_key: str
    openai_api_key: str | None = None
    whatsapp_api_url: str | None = None
    whatsapp_api_token: str | None = None
    tts_provider: str = "gtts"
    data_retention_days: int = 30
    ocr_engine: str = "pytesseract"

    class Config:
        env_file = ".env"

settings = Settings()