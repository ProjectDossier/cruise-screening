import logging
from typing import Dict

from flask import Flask, request
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.info("Loading model and tokenizer...")

tokenizer = AutoTokenizer.from_pretrained("bigscience/T0_3B")
logging.info("Tokenizer loaded")

model = AutoModelForSeq2SeqLM.from_pretrained("bigscience/T0_3B")
model.to("cuda")
logging.info("Model loaded")


def get_response(text: str) -> str:
    inputs = tokenizer.encode(text, return_tensors="pt")
    inputs = inputs.to("cuda")
    outputs = model.generate(inputs, max_length=32, num_beams=4, early_stopping=True)
    out_text = tokenizer.decode(outputs[0].to("cpu"))

    out_text = out_text.replace("<pad>", "")
    out_text = out_text.replace("<s>", "")
    out_text = out_text.replace("</s>", "")
    return out_text.strip()


@app.route("/")
def index():
    page = """
    <html>
    <head>
    <title>Text to text models server</title>
    <style>
        .code {
            background-color: #f8f8f8;
            border: 1px solid #e8e8e8;
            border-radius: 3px;
            font-family: monospace;
            font-size: 14px;
            line-height: 1.42857;
            margin: 0;
            overflow: auto;
            padding: 9.5px;
            word-break: normal;
            word-wrap: normal;
        }
    </style>
    </head>
    <body>
    <h1>Text to text models server</h1>
    <p>Route: <span class="code">/summarize</span></p>
    <p>Methods allowed: <span class="code">POST</span></p>
    <p>POST data: <span class="code">{"text": "text to be summarized"}</span></p>
    <p>POST response: <span class="code">{"response": "summary of the text"}</span></p>
    <hr />
    <p>Route: <span class="code">/question</span></p>
    <p>Methods allowed: <span class="code">POST</span></p>
    <p>POST data: <span class="code">{"text": "Your question"}</span></p>
    <p>POST response: <span class="code">{"response": "Models answer", "status": "status_string"}</span></p>
    <hr />    
    <p>Models supported: <span class="code">bigscience/T0_3B</span></p>
    </body>
    </html>
    """
    return page


@app.route("/summarize", methods=["POST"])
def summarize() -> Dict:
    if request.method == "POST":
        in_data = request.get_json()
        text = in_data["text"]
        out_text = get_response(f"Summarise the following text: {text}")
    else:
        out_text = "Only POST allowed"
    return {"results": out_text}


@app.route("/question", methods=["POST"])
def question() -> Dict[str, str]:
    if request.method != "POST":
        return {"response": "Only POST allowed", "status": "ERROR"}

    text = request.json["text"]
    try:
        response = get_response(text)
        status = "OK"
    except Exception as e:
        logging.error(e)
        response = "Error"
        status = "ERROR"
    return {"response": response, "status": status}


logging.info("App started")
logging.info("Waiting for requests at /search")
