"""Logging configuration for the project."""
import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from rich.console import Console
from rich.logging import RichHandler
from rich import traceback


def setup_logging():
    """Setup logging."""
    sys.stdout.reconfigure(encoding="utf-8")
    console = Console()
    traceback.install(console=console, show_locals=False)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)
    # create logger
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)  # set log level

    # create formatter
    CLI_FORMAT = "%(message)s"
    FILE_FORMAT = "%(asctime)s - %(levelname)-8s - %(message)s - %(filename)s - %(lineno)d - %(name)s"

    # create file handler
    LOG_FILENAME = "manhua-dl.log"
    LOG_DIR = "./logs"
    os.makedirs(LOG_DIR, exist_ok=True)
    LOG_FILEPATH = os.path.join(LOG_DIR, LOG_FILENAME)
    file_handler = RotatingFileHandler(
        LOG_FILEPATH, maxBytes=1000000, backupCount=10, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(FILE_FORMAT))

    console_handler = RichHandler(
        level=logging.WARNING,
        console=console,
        rich_tracebacks=True,
        tracebacks_show_locals=False,
        markup=True,
    )
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(logging.Formatter(CLI_FORMAT))
    log.addHandler(file_handler)
    log.addHandler(console_handler)
    return log
