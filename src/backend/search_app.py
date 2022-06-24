import json
import logging

import requests
from flask import Flask, request

app = Flask(__name__)


##########################################################
### CONFIG
##########################################################

CONFIG_PATH = "/config/search_app_config.json"

with open(CONFIG_PATH, "r") as fp:
    config = json.load(fp)


def build_query(query_text:str, top_k:int):
    """"""
    data_json = {
        "size": top_k,
        "query": {
            "bool": {
                "should": [
                    {
                        "match": {
                            "document": query_text
                        }
                    }
                ],  # this is not document this is abstract
                "minimum_should_match": 0,
                "boost": 1.0,
            },
        },
        "highlight": {"fields": {"document": {}}},
    }
    data_json = {
        "size": top_k,
        "query": {
            "bool": {
                "should": [
                    {
                        "multi_match": {
                            "query": query_text,
                            "fields": ["title", "abstract", "authors"]
                        }
                    }
                ]
            }
        },
        "highlight": {"fields": {"document": {}}},
    }
    return data_json


def search_es(query: str, index_name: str, top_k: int):
    host = config["host"]
    # use the query builder to create the elastic search json query object
    query_data = build_query(query, top_k=top_k)
    data_json = json.dumps(query_data)
    headers = {
        "Content-type": "application/json",
    }
    r = requests.post(
        host + "/" + ",".join([index_name]) + "/_search",
        data=data_json,
        headers=headers,
    )
    results = r.json()
    return results, query_data


@app.route("/search", methods=["POST"])
def search():
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


logging.info(f"API running...")
