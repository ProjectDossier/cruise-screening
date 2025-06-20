from typing import Any

import yaml


def get_config() -> dict[str, Any]:
    with open("./config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)