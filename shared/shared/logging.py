import logging
import sys
from .config import settings

def setup_logging():
    """
    Configures the root logger for the application.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    if settings.DEBUG:
        logging.getLogger("shared").setLevel(logging.DEBUG)
        logging.getLogger("services").setLevel(logging.DEBUG)
    
    noisy_libs = [
        "httpcore",
        "httpx",
        "openai",
        "urllib3",
        "uvicorn.access",
        "uvicorn.error"
    ]

    for lib in noisy_libs:
        logging.getLogger(lib).setLevel(logging.WARNING)