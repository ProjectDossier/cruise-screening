from os import environ

from google import genai
from waitress import serve

from ecriteria.config import get_config
from ecriteria.flask import init_app, init_basic_endpoints
from ecriteria.logging import init_logging
from ecriteria_external.endpoints import create_generate_pico


def main() -> None:
    config = get_config()

    init_logging(config)
    app = init_app(__name__, config)
    init_basic_endpoints(app)

    client = genai.Client(api_key=environ.get("API_KEY"))
    app.route('/generate_pico', methods=['POST'])(create_generate_pico(app, client))

    serve(app=app,
          host=app.config.get('HOST', '127.0.0.1'),
          port=app.config.get('PORT', 5000))

if __name__ == "__main__":
    main()