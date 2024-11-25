import json
import logging
from typing import Dict

import requests
from flask import Flask, request, render_template

app = Flask(__name__)

##########################################################
### CONFIG
##########################################################

CONFIG_PATH = "/config/search_app_config.json"

with open(CONFIG_PATH, "r") as fp:
    config = json.load(fp)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)


def build_query(query_text: str, top_k: int):
    """"""
    return {
        "size": top_k,
        "query": {
            "bool": {
                "should": [
                    {
                        "multi_match": {
                            "query": query_text,
                            "fields": ["title", "abstract", "authors.name"],
                        }
                    }
                ],
                "minimum_should_match": 0,
                "boost": 1.0,
            }
        },
        "highlight": {"fields": {"abstract": {}, "title": {}, "authors.name": {}}},
    }


def search_es(query: str, index_name: str, top_k: int):
    host = config["host"]
    # use the query builder to create the elastic search json query object
    query_data = build_query(query_text=query, top_k=top_k)
    data_json = json.dumps(query_data)
    headers = {
        "Content-type": "application/json",
    }
    r = requests.post(
        f"{host}/" + ",".join([index_name]) + "/_search",
        data=data_json,
        headers=headers,
    )
    results = r.json()
    return results, query_data


@app.route("/api/v1/search", methods=["POST"])
def search() -> Dict[str, str]:
    if request.method == "POST":
        in_data = request.get_json()
        query = in_data["query"]
        es_index = in_data["es_index"]
        es_top_k = int(in_data["es_top_k"])
        results, query_data = search_es(query, index_name=es_index, top_k=es_top_k)
    else:
        results = "Only POST allowed"
        query_data = {}
    return {"results": results, "query": query_data}


@app.route("/api/v1/status", methods=["GET"])
def status() -> Dict[str, str]:
    """Return the status of the API and underlying elasticsearch."""
    host = config["host"]
    try:
        r = requests.get(f"{host}/_cat/health")
    except requests.exceptions.ConnectionError:
        return {"status": "ERROR", "message": "Connection error to ElasticSearch"}
    return {"status": "OK", "message": r.text}


@app.route("/api/v1/indices", methods=["GET"])
def indices() -> Dict[str, str]:
    def _convert_response_to_json(response_content: str):
        lines = response_content.split("\n")
        lines = lines[1:]  # remove header row
        lines = [line for line in lines if line]  # remove empty lines
        _indices_status = []
        for line in lines:
            fields = line.split()
            index = {
                "health": fields[0],
                "status": fields[1],
                "index": fields[2],
                "uuid": fields[3],
                "pri": fields[4],
                "rep": fields[5],
                "docs_count": fields[6],
                "docs_deleted": fields[7],
                "store_size": fields[8],
                "pri_store_size": fields[9],
            }
            _indices_status.append(index)
        return _indices_status

    if request.method == "GET":
        host = config["host"]
        r = requests.get(f"{host}/_cat/indices?v")
        return {
            "status": "OK",
            "indices": _convert_response_to_json(r.content.decode()),
        }
    else:
        return {"status": "ERROR", "message": "Only GET allowed"}


@app.route("/api/v1/add_docs", methods=["POST"])
def add_docs() -> Dict[str, str]:
    if request.method == "POST":
        host = config["host"]

        in_data = request.get_json()
        docs = in_data["docs"]
        index_name = in_data["index_name"]

        # check if index exists
        r = requests.get(f"{host}/_cat/indices?v")
        indices = r.content.decode().split("\n")
        indices = [i.split()[2] for i in indices[1:-1]]
        if index_name not in indices:
            mapping = {
                "mappings": {
                    "properties": {
                        "keywords": {"type": "object", "enabled": "false"},
                        "CSO_keywords": {"type": "object", "enabled": "false"},
                    }
                }
            }
            r = requests.put(f"{host}/{index_name}", json=mapping)
            logging.info(f"Created index {index_name} with mapping {mapping}")

        r = requests.post(
            f"{host}/{index_name}/_bulk",
            data=docs,
            headers={"Content-Type": "application/json"},
        )
        return {"status": "OK", "message": r.text}
    else:
        return {"status": "ERROR", "message": "Only POST allowed"}


@app.route("/api/v1/create_index", methods=["POST"])
def create_index() -> Dict[str, str]:
    """Check if index exist with a provided index_name.
    If not, then create the index with the provided index_name."""
    if request.method != "POST":
        return {"status": "ERROR", "message": "Only POST allowed"}
    in_data = request.get_json()
    index_name = in_data["index_name"]

    index_config = {
        "mappings": {
            "properties": {
                "id": {"type": "text"},
                "contents": {
                    "type": "text",
                    "analyzer": "whitespace",
                    "similarity": "ranking_function",
                },
            }
        },
        "settings": {
            "number_of_shards": 1,
            "index": {
                "similarity": {
                    "ranking_function": {"type": "BM25", "b": 0.75, "k1": 1.2}
                }
            },
        },
    }
    host = config["host"]

    r = requests.get(f"{host}/_cat/indices?v")
    indices = r.content.decode().split("\n")
    indices = [i.split()[2] for i in indices[1:-1]]

    if index_name not in indices:
        r = requests.put(f"{host}/{index_name}", json=index_config)
        logging.info(f"Created index {index_name} with mapping {index_config}")
        return {"status": "OK", "message": r.text}

    logging.warning(f"Index {index_name} already exists")
    return {"status": "OK", "message": "index already exists"}


@app.route("/")
def home():
    return render_template("index.html")


logging.info("API running...")
