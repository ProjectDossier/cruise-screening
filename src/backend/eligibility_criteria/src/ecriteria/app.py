import yaml
from flask import Flask, request, Response
import requests # Keep requests for now, though it will be replaced for Gemini
import os
import xml.etree.ElementTree as ET
import logging
import logging.config
import google.generativeai as genai # Import the Gemini library

app = Flask(__name__)

# Ensure logs directory and app.log file exist
log_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "app.log")
if not os.path.exists(log_file):
    with open(log_file, "w"):
        pass

# Load YAML config
with open("flask/config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Set config values
for key, value in config.items():
    if key != "logging":
        app.config[key.upper()] = value

# Setup logging
if "logging" in config:
    logging.config.dictConfig(config["logging"])
else:
    logging.basicConfig(level=logging.ERROR)

# Configure the Generative AI model
# Use the API key from config for development, consider environment variables for production
genai.configure(api_key=config["api_key"])
model = genai.GenerativeModel(config["api_url"]) # config["api_url"] will now hold "gemini-1.5-flash"

@app.errorhandler(413)
def request_entity_too_large(error):
    app.logger.error(f"Payload too large: {error}")
    return Response("<error>Request too large. Limit is 8192 bytes.</error>", status=413, mimetype='application/xml')

@app.route('/validate', methods=['POST'])
def validate():
    max_length = app.config.get('MAX_CONTENT_LENGTH', 8192)
    if max_length and len(request.data) > max_length:
        return Response("<error>Request too large. Limit is 8192 bytes.</error>", status=413, mimetype='application/xml')

    try:
        tree = ET.fromstring(request.data)
        if tree.tag != "request":
            raise ValueError("Root tag must be <request>.")

        xml_input_elem = tree.find("xml_input")
        if xml_input_elem is None:
            raise ValueError("Missing <xml_input> section.")

        abstract_elem = xml_input_elem.find("article_abstract")
        if abstract_elem is None:
            raise ValueError("Missing <article_abstract> inside <xml_input>.")

        valid_tags = {
            "article_title", "background", "objectives",
            "selection_criteria", "main_results", "authors_conclusions",
            "search_methods", "data_collection_and_analysis"
        }

        for child in abstract_elem:
            if child.tag not in valid_tags:
                raise ValueError(f"Invalid tag found in <article_abstract>: <{child.tag}>")
            if child.tail and child.tail.strip():
                raise ValueError(f"Unexpected text after tag <{child.tag}>")

        if abstract_elem.tail and abstract_elem.tail.strip():
            raise ValueError("Unexpected text found after <article_abstract>")

        xml_input_str = ET.tostring(xml_input_elem, encoding='unicode', method='xml')
        inner_xml = xml_input_str.replace('<xml_input>', '').replace('</xml_input>', '').strip()
        response_xml = f"<validated>{inner_xml}</validated>"
        return Response(response_xml, mimetype='application/xml')

    except Exception as e:
        app.logger.exception("Validation error")
        error_xml = f"<error>Invalid XML input: {str(e)}</error>"
        return Response(error_xml, status=400, mimetype='application/xml')

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

        # Call the Gemini API using the google-generativeai library
        chat_session = model.start_chat(
            history=[
                {"role": "user", "parts": [instruction]},
                {"role": "model", "parts": ["Ok, I understand. Send me the abstract."]} # Acknowledgment from model (optional, good for chat context)
            ]
        )
        response = chat_session.send_message(inner_xml)
        answer = response.text.strip()

        return Response(f"<response><answer>{answer}</answer></response>", mimetype='application/xml')

    except Exception as e:
        app.logger.exception("Inference error")
        return Response(f"<error>{str(e)}</error>", status=500, mimetype='application/xml')

@app.route('/generate', methods=['POST'])
def generate_combined():
    try:
        with app.test_request_context('/validate', method='POST', data=request.data):
            validate_response = validate()
            
        if validate_response.status_code != 200:
            return validate_response

        app.logger.info("Validation successful")
        validated_xml = validate_response.get_data(as_text=True)

        with app.test_request_context('/_infer', method='POST', data=validated_xml, environ_base={'REMOTE_ADDR': '127.0.0.1'}):
            infer_response = infer()

        return infer_response

    except Exception as e:
        app.logger.exception("Unexpected failure in generate_combined")
        return Response(f"<error>Unexpected failure: {str(e)}</error>", status=500, mimetype='application/xml')


def main() -> None:
    app.run(
        host=config.get('host', '127.0.0.1'),
        port=config.get('port', 5000),
        debug=config.get('debug', False)
    )

if __name__ == "__main__":
    main()