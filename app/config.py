from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RAG Knowledge Assistant"
    env: str = "development"
    api_key: str = "change-me"
    openai_api_key: str = ""
    openai_chat_model: str = "gpt-5-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    embedding_dim: int = 1536
    database_url: str = "postgresql+psycopg://rag:rag@localhost:5432/rag"
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl_seconds: int = 300
    max_file_bytes: int = 10 * 1024 * 1024
    chunk_size_words: int = 260
    chunk_overlap_words: int = 50
    top_k: int = 6

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
