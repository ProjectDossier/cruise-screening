from django.contrib.auth.models import User
from datetime import datetime
import functools
import operator
import secrets
import random
import csv
import os
import re
from elasticsearch import Elasticsearch


class ES_conn():

    def __init__(self):
        self.client = None
        self.start_connection()

    def start_connection(self):
        self.client = Elasticsearch("http://localhost:9200")

    #def search(self,user_request: str):
    #    print(self.client.info())

    # ES server needs to exist already, index needs to exist already


elastic_server = ES_conn()
elastic_server.start_connection()


def search(query, index, top_k):

    bool_query = {
        "size": top_k,
        "query": {
            "bool": {
                "should": [
                    {"match": {'content': query}}
                ]
                , "minimum_should_match": 0,
                "boost": 1.0
            }
        }
    }

    candidates = elastic_server.client.search(index=index, body=bool_query)

    candidate_list = []
    for candidate in candidates['hits']['hits']:
        candidate_list.append({'id': candidate["_id"], 'content': candidate['_source'].get('content')})

    return candidate_list



# search function (input from user, give back output from elasticsearch)
