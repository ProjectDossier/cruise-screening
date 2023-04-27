import json
from collections import deque

import requests
from elasticsearch import helpers, Elasticsearch


class LexicalSearch:
    def __init__(self, data: list, tax_name: str):
        self.data = data
        self.index_name = f"taxonomy_{tax_name.lower()}_index"
        # self.es_client = Elasticsearch(timeout=180)
        self.check_index()

        self.get_index()

    def check_index(self) -> bool:
        """Check if index exists, if not create it. If creates index, then index the data.
        Returns: True if index exists or was created, False otherwise."""
        res = requests.get(
            "http://localhost:9880/api/v1/indices",
        )
        if res.status_code != 200:
            return False
        indices = [x['index'] for x in res.json()['indices']]
        if self.index_name in indices:
            return True
        headers = {"Content-type": "application/json"}
        res = requests.post(
            "http://localhost:9880/api/v1/concept_search/create_lexical_index",
            data=json.dumps(
                {
                    "index_name": self.index_name,
                }
            ),
            headers=headers,
        )
        res = requests.post(
            "http://localhost:9880/api/v1/concept_search/add_concepts",
            data=json.dumps(
                {
                    "index_name": self.index_name,
                    "concepts": self.data,
                }
            ),
            headers=headers,
        )

        return res.status_code == 200

    # def doc_generator(self):
    #     for idx, text in enumerate(self.data):
    #         yield {"_index": self.index_name, "_source": {"id": idx, "document": text}}
    #
    # def get_index(self, index_config=None, threads=8):
    #     if index_config is None:
    #         index_config = {
    #             "mappings": {
    #                 "properties": {
    #                     "id": {"type": "text"},
    #                     "contents": {
    #                         "type": "text",
    #                         "analyzer": "whitespace",
    #                         "similarity": "ranking_function",
    #                     },
    #                 }
    #             },
    #             "settings": {
    #                 "number_of_shards": 1,
    #                 "index": {
    #                     "similarity": {
    #                         "ranking_function": {"type": "BM25", "b": 0.75, "k1": 1.2}
    #                     }
    #                 },
    #             },
    #         }
    #
    #     # self.es_client.indices.delete(index=self.index_name, ignore=[400, 404])
    #     try:
    #         self.es_client.indices.create(index=self.index_name, body=index_config)
    #     except:
    #         pass
    #
    #     try:
    #         deque(
    #             helpers.parallel_bulk(
    #                 self.es_client,
    #                 self.doc_generator(),
    #                 thread_count=threads,
    #                 chunk_size=500,
    #                 raise_on_error=True,
    #                 request_timeout=10000,
    #             ),
    #             maxlen=0,
    #         )
    #     except RuntimeError as e:
    #         print(e)

    def lexical_search(self, query):
        # res = self.es_client.search(
        #     index=self.index_name,
        #     body={"size": 1, "query": {"match": {"document": query}}},
        # )["hits"]["hits"][0]
        #
        # score = res["_score"]
        # res = res["_source"]["id"]
        #
        # if score > 7:
        #     return res
        # else:
        #     return -100
        # replace with call to api/v1/concept_search/lexical_search
        headers = {"Content-type": "application/json"}
        r = requests.post(
            f"http://localhost:9880/api/v1/concept_search/lexical_search",
            data=json.dumps(
                {
                    "query": {
                        "match": {
                            "document": query,
                        }
                    },
                    "size": 1,
                    "index_name": self.index_name,
                }
            ),
            headers=headers,
        )
        if r.status_code != 200:
            return -100
        res = r.json()["hits"]["hits"][0]
        score = res["_score"]
        res = res["_source"]["id"]
        if score > 7:
            return res
        else:
            return -100
