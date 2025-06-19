import logging.config
import os
import xml.etree.ElementTree as ET

import torch
import yaml
from flask import Flask, request, Response
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig

app = Flask(__name__)

# Ensure logs directory and app.log file exist
log_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "app.log")
if not os.path.exists(log_file):
    with open(log_file, "w"):
        pass
    
with open("./config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Set Flask config from YAML
for key, value in config.items():
    if key != "logging": 
        app.config[key.upper()] = value

# Setup logging
if "logging" in config:
    logging.config.dictConfig(config["logging"])
else:
    logging.basicConfig(level=logging.ERROR)


for key, value in config.items():
    app.config[key.upper()] = value


MODEL_PATH = config.get("model_path", "flask/model/")
if torch.cuda.is_available():
    device = torch.device("cuda")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForCausalLM.from_pretrained(MODEL_PATH)
    gen_config = GenerationConfig.from_pretrained(MODEL_PATH)
else:
    device = None
    tokenizer = None
    model = None

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
            "selection_criteria", "main_results", "authors_conclusions", "search_methods", "data_collection_and_analysis"
        }

        for child in abstract_elem:
            if child.tag not in valid_tags:
                raise ValueError(f"Invalid tag found in <article_abstract>: <{child.tag}>")
            if child.tail and child.tail.strip():
                raise ValueError(f"Unexpected text after tag <{child.tag}>")

        if abstract_elem.tail and abstract_elem.tail.strip():
            raise ValueError("Unexpected text found after <article_abstract>")

        # Clean & return valid XML
        xml_input_str = ET.tostring(xml_input_elem, encoding='unicode', method='xml')
        inner_xml = xml_input_str.replace('<xml_input>', '').replace('</xml_input>', '').strip()

        # Return wrapped XML ready for next step
        response_xml = f"<validated>{inner_xml}</validated>"
        return Response(response_xml, mimetype='application/xml')

    except Exception as e:
        app.logger.exception("Validation error")
        error_xml = f"<error>Invalid XML input: {str(e)}</error>"
        return Response(error_xml, status=400, mimetype='application/xml')

@app.route('/_infer', methods=['POST'])
def infer():
    remote_ip = request.remote_addr or ""
    if not (remote_ip.startswith("127.") or remote_ip.startswith("192.168.")):
        return Response("<error>Unauthorized</error>", status=403, mimetype='application/xml')

    if not torch.cuda.is_available():
        return Response("<error>CUDA is not available.</error>", status=400, mimetype='application/xml')

    try:
        # Accept raw validated XML wrapped in <validated>...</validated>
        tree = ET.fromstring(request.data)
        if tree.tag != "validated":
            raise ValueError("Root tag must be <validated>.")

        inner_xml = ET.tostring(tree, encoding='unicode', method='xml')
        inner_xml = inner_xml.replace("<validated>", "").replace("</validated>", "").strip()

        messages = [
            {"role": "system", "content": config["instruction"]},
            {"role": "user", "content": inner_xml},
        ]

        prompt = tokenizer.apply_chat_template(
            messages, tokenize = False
        )
        prompt_length = len(prompt)


        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        output = model.generate(
            **inputs,
            max_new_tokens=config["model_max_new_tokens"],
            generation_config=gen_config
        )

        decoded = tokenizer.decode(output[0], skip_special_tokens=True)
        answer = decoded.strip()
        answer_prompt = answer[prompt_length:]

        app.logger.info("Inference successful")
        return Response(f"<response><answer>{answer_prompt}</answer></response>", mimetype='application/xml')

    except Exception as e:
        app.logger.exception("Inference error")
        return Response(f"<error>{str(e)}</error>", status=500, mimetype='application/xml')


@app.route('/generate', methods=['POST'])
def generate_combined():
    try:
        # Validate the XML via local function call
        with app.test_request_context('/validate', method='POST', data=request.data,):
            validate_response = validate()
        
        if validate_response.status_code != 200:
            return validate_response  # return validation error as-is

        app.logger.info("Validation successful")
        validated_xml = validate_response.get_data(as_text=True)

        #Inference call using local dispatch
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
