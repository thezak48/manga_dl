"""Logging configuration for the project."""
import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler

from rich import traceback
from rich.console import Console
from rich.logging import RichHandler


def setup_logging(dirname):
    """Setup logging."""
    sys.stdout.reconfigure(encoding="utf-8")
    console = Console()
    traceback.install(console=console, show_locals=False)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)

    cli_format = "%(message)s"
    file_format = "%(asctime)s - %(levelname)-8s - %(message)s - %(filename)s - %(lineno)d - %(name)s"

    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"manga_dl_{current_time}.log"
    log_dir = f"./{dirname}/logs"
    os.makedirs(log_dir, exist_ok=True)
    log_filepath = os.path.join(log_dir, log_filename)
    file_handler = RotatingFileHandler(
        log_filepath, maxBytes=1000000, backupCount=10, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(file_format))

    console_handler = RichHandler(
        level=logging.WARNING,
        console=console,
        rich_tracebacks=True,
        tracebacks_show_locals=False,
        markup=True,
    )
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(logging.Formatter(cli_format))
    log.addHandler(file_handler)
    log.addHandler(console_handler)
    return log
