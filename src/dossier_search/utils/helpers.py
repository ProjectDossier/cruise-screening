from elasticsearch import Elasticsearch
import requests


def search(query: str, index: str, top_k: int):
    headers = {
        'Content-type': 'application/json'
    }
    res = requests.post( 'localhost:9880' + '/search', data={'query': query}, headers=headers)
    results = res.json()['results']
    candidate_list = []
    for candidate in results["hits"]["hits"]:
        candidate_list.append(
            {"id": candidate["_id"], "content": candidate["_source"].get("document")}
        )

    return candidate_list
