from loguru import logger
import sys
from pathlib import Path


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


def setup_logger():
    logger.remove()

    logger.add(
        sys.stdout,
        level="INFO",
        format="{time} | {level} | {message}",
    )

    logger.add(
        LOG_DIR / "app.log",
        level="INFO",
        rotation="10 MB",
        retention=5,
        compression="zip",
        serialize=True,
    )

    logger.add(
        LOG_DIR / "error.log",
        level="ERROR",
        rotation="10 MB",
        retention=5,
        compression="zip",
        serialize=True,
    )

    logger.add(
        LOG_DIR / "access.log",
        level="INFO",
        rotation="10 MB",
        retention=5,
        compression="zip",
        serialize=True,
        filter=lambda record: record["message"] == "HTTP request",
    )