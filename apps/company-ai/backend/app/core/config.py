from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "company-ai"
    APP_VERSION: str = "0.1.0"
    
    # Database
    DATABASE_URL: str = "postgresql+psycopg2://companyai_user:FTL%401234@localhost:5432/companyai"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # JWT
    JWT_SECRET_KEY: str = "change_me_in_production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24
    
    # File Upload
    DATA_DIR: str = "/home/aiapp/data"
    UPLOAD_DIR: str = "/home/aiapp/data/uploads"
    MAX_UPLOAD_MB: int = 25
    ALLOWED_EXTENSIONS: list = ["pdf", "docx", "txt"]
    
    # Ollama Embeddings
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text"
    
    # Ollama Chat / RAG
    OLLAMA_CHAT_MODEL: str = "llama3.1:8b"
    RAG_TOP_K: int = 5
    RAG_MAX_CONTEXT_CHARS: int = 6000
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def max_upload_bytes(self) -> int:
        """Calculate max upload size in bytes."""
        return self.MAX_UPLOAD_MB * 1024 * 1024


settings = Settings()
