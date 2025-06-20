from typing import Any

from flask import Flask

from ecriteria.endpoints import create_request_entity_too_large


def init_app(path: str, config: dict[str, Any]) -> Flask:
    app = Flask(path)

    for key, value in config.items():
        if key != "logging":
            app.config[key.upper()] = value

    return app

def init_basic_endpoints(app) -> None:
    app.errorhandler(413)(create_request_entity_too_large(app))