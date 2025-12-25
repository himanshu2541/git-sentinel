from shared.config import Settings as SharedSettings
from typing import Optional

class Settings(SharedSettings):

    LLM_MODEL_PROVIDER: str = "local"  # or "azure", "anthropic", etc.
    LLM_MODEL_NAME: str = "phi-3-mini-4k-instruct"
    LLM_BASE_URL: Optional[str] = "http://localhost:1234/v1" # For local or custom providers
    LLM_TEMPERATURE: float = 0.5
    LLM_API_KEY: str = ""
    LLM_MAX_TOKENS: int = 2048

settings = Settings()