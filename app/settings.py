from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "dev"
    collection_name: str = "runbooks"
    top_k: int = 5

    ollama_base_url: str = "http://ollama:11434"
    ollama_chat_model: str = "llama3.1"
    ollama_embed_model: str = "nomic-embed-text"

    postgres_dsn: str = "postgresql+psycopg://app:app@postgres:5432/app"

settings = Settings()
