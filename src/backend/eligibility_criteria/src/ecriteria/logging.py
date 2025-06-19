import logging
from logging.config import dictConfig
from typing import Any


def init_logging(config: dict[str, Any]) -> None:
    if "logging" in config:
        dictConfig(config["logging"])
        return

    logging.basicConfig(level=logging.ERROR)
