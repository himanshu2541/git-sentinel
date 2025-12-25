from shared.config import Settings as SharedSettings

class Settings(SharedSettings):
    ENV: str = SharedSettings().ENV
    RELOAD: bool = ENV != "production"
    LOG_LEVEL: str = "info" if ENV == "production" else "debug"

    API_GATEWAY_HOST: str = "localhost"
    API_GATEWAY_PORT: int = 8000
    
settings = Settings()