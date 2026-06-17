from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # LLM
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.1-8b-instant"

    # Database
    DATABASE_URL: str

    # Vector DB
    CHROMA_PATH: str = "./backend/storage/vector_db"
    CHROMA_COLLECTION: str = "skb_chunks"

    # File Storage
    UPLOAD_DIR: str = "./backend/storage/files"

    # Chunking
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 100

    # Retrieval
    CANDIDATE_TOP_K: int = 20
    FINAL_TOP_K: int = 5
    VECTOR_WEIGHT: float = 0.7
    KEYWORD_WEIGHT: float = 0.3

    # Limits
    MAX_FILE_SIZE_MB: int = 50
    MAX_PAGES_PER_DOC: int = 150
    MAX_SESSIONS: int = 10

    # Security
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 480

    model_config = SettingsConfigDict(
        env_file="../.env",
        case_sensitive=True
    )


settings = Settings()