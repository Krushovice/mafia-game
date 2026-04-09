"""Logging configuration for the application."""

import logging
import logging.handlers
from pathlib import Path


def setup_logging(level: str = "INFO", fmt: str = "%(asctime)s %(levelname)s %(name)s: %(message)s", log_dir: str = "logs") -> None:
    """Configure logging with both console and file handlers.

    Creates:
        - logs/app.log — all messages (rotating, 10 MB max per file, 5 backups)
        - logs/error.log — errors and above only (rotating, 10 MB max, 5 backups)
    """
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    formatter = logging.Formatter(fmt)

    # Root logger
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Console handler
    console = logging.StreamHandler()
    console.setLevel(getattr(logging, level.upper(), logging.INFO))
    console.setFormatter(formatter)
    root.addHandler(console)

    # Rotating file handler — all logs
    all_handler = logging.handlers.RotatingFileHandler(
        log_path / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8",
    )
    all_handler.setLevel(logging.DEBUG)
    all_handler.setFormatter(formatter)
    root.addHandler(all_handler)

    # Rotating file handler — errors only
    error_handler = logging.handlers.RotatingFileHandler(
        log_path / "error.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root.addHandler(error_handler)
