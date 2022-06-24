"""Simple script for adding documents to the elastic db"""
import json
import argparse

from elasticsearch import Elasticsearch
from tqdm.auto import tqdm


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data_path",
        type=str,
        default="../data/AMiner_sample.jsonl",
        help="path to the file containing data which should be added to the index. "
        "Only jsonl format is supported.",
    )
    parser.add_argument("--port", type=int, default=9200, help="ES server port.")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="ES server host.")
    parser.add_argument(
        "--index", type=str, default="papers", help="Name of the ES index."
    )
    parser.add_argument(
        "--doc_type", type=str, default="aminer", help="Name of the ES doc type."
    )

    parser.add_argument(
        "--first_n_docs",
        type=int,
        default=10000,
        help="Number of first documents from the file that will be indexed in the ES."
        "If first_n_docs is equal to 0, then script indexes all docs.",
    )

    args = parser.parse_args()

    if not args.data_path.endswith(".jsonl"):
        raise ValueError("data_file should be in a jsonl format")

    with open(args.data_path) as fp:
        docs_list = list(fp)

    if isinstance(args.first_n_docs, int) and args.first_n_docs > 0:
        docs_list = docs_list[: args.first_n_docs]

    es = Elasticsearch([{"host": args.host, "port": args.port}])

    if not es.indices.exists(index=args.index):
        mapping = {
            "mappings": {
                "properties": {
                    "keywords": {"type": "object",  "enabled": "false"},
                    "CSO_keywords": {"type": "object", "enabled": "false"},
                }
            }
        }
        response = es.indices.create(
            index=args.index, body=mapping
        )

    for index_i, json_str in tqdm(enumerate(docs_list)):
        item = json.loads(json_str)
        res = es.index(index=args.index,
                       document=item)
