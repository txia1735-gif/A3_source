import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(app) -> None:
    if getattr(app, "_logging_ready", False):
        return

    log_dir = Path(app.config["LOG_DIR"])
    log_dir.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(name)s: %(message)s"
    )
    level = getattr(logging, app.config.get("LOG_LEVEL", "INFO").upper(), logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    app_file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=1_048_576,
        backupCount=5,
        encoding="utf-8",
    )
    app_file_handler.setLevel(level)
    app_file_handler.setFormatter(formatter)

    error_file_handler = RotatingFileHandler(
        log_dir / "error.log",
        maxBytes=1_048_576,
        backupCount=5,
        encoding="utf-8",
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(app_file_handler)
    root_logger.addHandler(error_file_handler)

    app.logger.handlers.clear()
    app.logger.setLevel(level)
    app.logger.propagate = True
    app._logging_ready = True

