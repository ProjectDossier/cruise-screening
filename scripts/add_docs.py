"""Simple script for adding documents to the elastic db"""
from elasticsearch import Elasticsearch
from tqdm.auto import tqdm
import json

FIRST_N_DOCS = 1000
PORT = 9205
HOST = "127.0.0.1"

es = Elasticsearch([{"host": HOST, "port": PORT}])

docs_list = []
with open("../data/AMiner_sample.jsonl") as fp:
    json_list = list(fp)


for index_i, json_str in tqdm(enumerate(json_list[:FIRST_N_DOCS])):
    item = json.loads(json_str)
    res = es.index(index="papers", doc_type="aminer", document=item)
