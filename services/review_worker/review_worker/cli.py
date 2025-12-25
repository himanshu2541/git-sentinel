import sys
import asyncio

from review_worker.worker import main as start_worker
from shared.logging import setup_logging

import logging
setup_logging()

logger = logging.getLogger(__name__)


def run():
    """
    Entry point to start the Review Worker.
    """
    logger.info(f"Starting Review Worker...")
    logger.info(f"Listening to Queue: review_jobs")

    try:
        asyncio.run(start_worker())
    except asyncio.CancelledError:
        logger.info("Review Worker Cancelled. Shutting down...")
    except KeyboardInterrupt:
        logger.info("Review Worker stopped manually.")
    except Exception as e:
        logger.error(f"Review Worker crashed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run()
