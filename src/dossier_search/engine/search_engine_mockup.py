from typing import List, Dict
from utils.article import Article


res1 = {"id": "53e99784b7602d9701f3e15d", "title": "Timing yield estimation", "url": "https://www.", "snippet": "str", "abstract": "str", "authors": "Michalarias, Omelchenko, Lenz", "publication_date": "str", "venue": "{'sid': 'data-and-knowledge-engineering', 'issn': '0169-023X', 't': 'J', 'raw': 'Data & Knowledge Engineering', 'publisher': 'North-Holland'}"}
res2 = {"id": "53e99784b7602d9701f3f411", "title": "Using XML to Integrate ", "url": "https://www.", "snippet": "str", "abstract": "str", "authors": "Pan, Chu, Zhou", "publication_date": "str", "venue": "{'id': '53a72e2020f7420be8c80142', 'name_d': 'International Symposium on Circuits and Systems', 'type': 0, 'raw': 'ISCAS (3)'}"}
res3 = {"id": "53e99784b7602d9701f3f5fe", "title": "Research on resource allocation", "url": "https://www.", "snippet": "str", "abstract": "str", "authors": "Sneed", "publication_date": "str", "venue": "{'id': '53a72e9920f7420be8c93fac', 'name_d': 'Computer Software and Applications Conference', 'type': 0, 'raw': 'COMPSAC'}"}
res4 = {"id": "53e99784b7602d9701f3f95d", "title": "FCLOS", "url": "https://www.", "snippet": "str", "abstract": "str", "authors": "Thomas", "publication_date": "str", "venue": "{'sid': 'telematics-and-informatics', 'issn': '0736-5853', 't': 'J', 'raw': 'Telematics and Informatics', 'publisher': 'Pergamon'}"}


res1_article = Article(**res1)
res2_article = Article(**res2)
res3_article = Article(**res3)
res4_article = Article(**res4)

def search_eng_mockup() -> List[Article]:

    results_list = []
    results_list.append(res1_article)
    results_list.append(res2_article)
    results_list.append(res3_article)
    results_list.append(res4_article)
    return results_list
