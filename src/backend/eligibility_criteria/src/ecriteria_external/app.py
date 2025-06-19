import logging.config
import os
import xml.etree.ElementTree as ET
from pathlib import Path

from google import genai
import yaml
from flask import Flask, request, Response
from google.genai.types import HttpOptions

from ecriteria.endpoints import create_request_entity_too_large, generate_pico


def main() -> None:
    app = Flask(__name__)

    with open("flask/config.yaml", "r") as f:
        config = yaml.safe_load(f)

    Path(os.path.join(os.getcwd(), "logs", "app.log")).touch(exist_ok=True)

    for key, value in config.items():
        if key != "logging":
            app.config[key.upper()] = value

    if "logging" in config:
        logging.config.dictConfig(config["logging"])
    else:
        logging.basicConfig(level=logging.ERROR)

    client = genai.Client(http_options=HttpOptions(api_version="v1"), api_key=config["api_key"])

    model = genai.GenerativeModel(config["api_url"])

    app.errorhandler(413)(create_request_entity_too_large(app))

    @app.route('/_infer', methods=['POST'])
    def infer():
        remote_ip = request.remote_addr or ""
        if not (remote_ip.startswith("127.") or remote_ip.startswith("192.168.") or remote_ip.startswith("10.")):
            return Response("<error>Unauthorized</error>", status=403, mimetype='application/xml')

        try:
            tree = ET.fromstring(request.data)
            if tree.tag != "validated":
                raise ValueError("Root tag must be <validated>.")

            inner_xml = ET.tostring(tree, encoding='unicode', method='xml')
            inner_xml = inner_xml.replace("<validated>", "").replace("</validated>", "").strip()

            instruction = config["instruction"]

            chat_session = model.start_chat(
                history=[
                    {"role": "system", "parts": [instruction]},
                ]
            )
            response = chat_session.send_message(inner_xml)
            answer = response.text.strip()

            return Response(f"<response><answer>{answer}</answer></response>", mimetype='application/xml')

        except Exception as e:
            app.logger.exception("Inference error")
            return Response(f"<error>{str(e)}</error>", status=500, mimetype='application/xml')

    @app.route('/generate_pico', methods=['POST'])
    def generate_pico():
        try:
            with app.test_request_context('/validate', method='POST', data=request.data):
                validate_response = validate()

            if validate_response.status_code != 200:
                return validate_response

            app.logger.info("Validation successful")
            validated_xml = validate_response.get_data(as_text=True)

            with app.test_request_context('/_infer', method='POST', data=validated_xml,
                                          environ_base={'REMOTE_ADDR': '127.0.0.1'}):
                infer_response = infer()

            return infer_response

        except Exception as e:
            app.logger.exception("Unexpected failure in generate_combined")
            return Response(f"<error>Unexpected failure: {str(e)}</error>", status=500, mimetype='application/xml')

    app.run(
        host=config.get('host', '127.0.0.1'),
        port=config.get('port', 5000),
        debug=config.get('debug', False)
    )

if __name__ == "__main__":
    main()