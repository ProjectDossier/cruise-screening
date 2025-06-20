from typing import Callable

from flask import Response, Flask


def create_request_entity_too_large(app: Flask) -> Callable:
    def request_entity_too_large(error):
        app.logger.error(f"Payload too large: {error}")
        return Response("<error>Request too large. Limit is 8192 bytes.</error>", status=413,
                        mimetype='application/xml')

    return request_entity_too_large