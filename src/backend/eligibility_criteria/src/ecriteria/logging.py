import logging
from logging.config import dictConfig
from pathlib import Path
from typing import Any


def init_logging(config: dict[str, Any]) -> None:
    if "logging" in config:
        log_file_path = Path(config["logging"]["handlers"]["file"]["filename"])
        log_file_path.parent.mkdir(exist_ok=True)
        log_file_path.touch(exist_ok=True)

        dictConfig(config["logging"])
        return

    logging.basicConfig(level=logging.ERROR)