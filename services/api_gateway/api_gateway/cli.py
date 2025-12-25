import uvicorn
from api_gateway.config import settings
import logging

def run():
    logger = logging.getLogger(__name__)
    logger.info("Starting API Gateway...")
    uvicorn.run(
        "api_gateway.main:app",
        host=settings.API_GATEWAY_HOST,
        port=int(settings.API_GATEWAY_PORT),
        log_level=settings.LOG_LEVEL,
        reload=settings.RELOAD,
    )

if __name__ == "__main__":
    run()
