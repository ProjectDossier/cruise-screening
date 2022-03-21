from elasticsearch import Elasticsearch


class ES_connection:
    def __init__(self):
        self.client = None

    def start_connection(self, port: int = 9205, host: str = "127.0.0.1"):
        self.client = Elasticsearch([{"host": host, "port": port}])


elastic_server = ES_connection()
elastic_server.start_connection()


def search(query: str, index: str, top_k: int):
    bool_query = {
        "size": top_k,
        "query": {
            "bool": {
                "should": [{"match": {"document": query}}],
                "minimum_should_match": 0,
                "boost": 1.0,
            }
        },
    }

    candidates = elastic_server.client.search(index=index, body=bool_query)

    candidate_list = []
    for candidate in candidates["hits"]["hits"]:
        candidate_list.append(
            {"id": candidate["_id"], "content": candidate["_source"].get("document")}
        )

    return candidate_list
