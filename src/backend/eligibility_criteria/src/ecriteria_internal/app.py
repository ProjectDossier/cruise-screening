from waitress import serve

from ecriteria.config import get_config
from ecriteria.flask import init_app, init_basic_endpoints
from ecriteria.logging import init_logging
from ecriteria_internal.endpoints import create_generate_pico
from ecriteria_internal.model import ModelConfig


def main() -> None:
    config = get_config()

    init_logging(config)
    app = init_app(__name__, config)
    init_basic_endpoints(app)

    model = ModelConfig.from_config(app.config)
    app.logger.info("Model successfully loaded into VRAM")
    app.route('/generate_pico', methods=['POST'])(create_generate_pico(app, model))

    serve(app=app,
          host=app.config.get('HOST', '127.0.0.1'),
          port=app.config.get('PORT', 5000))


if __name__ == "__main__":
    main()