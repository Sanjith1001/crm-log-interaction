from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/crm"
    groq_api_key: str = ""
    groq_model_router: str = "gemma2-9b-it"
    groq_model_responder: str = "llama-3.3-70b-versatile"
    jwt_secret: str = "change-me"


settings = Settings()

