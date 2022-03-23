import requests
import json
from utils.article import Article


def highlighter(query: str, doc:str):
    keywords = query.split()
    sentence_pool = []
    for sentence in doc.split('.'):
        for key in keywords:
            if key in sentence:
                sentence = '<em>' + sentence + '</em>'
                break
        sentence_pool.append(sentence)
    highlighted_text = '.'.join(sentence_pool)
    return highlighted_text

def search(query: str, index: str, top_k: int):
    headers = {
        'Content-type': 'application/json'
    }
    res = requests.post( 'http://localhost:9880' + '/search', data=json.dumps({'query': query}), headers=headers)
    results = res.json()['results']
    candidate_list = []
    for candidate in results["hits"]["hits"]:
        doc_text = candidate["_source"].get("document")
        if doc_text:
            abstract = highlighter(query, doc_text)
            snippet = abstract[:160] # doc_text[:160]
        else:
            abstract = ""
            snippet = ""
        authors_raw = candidate["_source"].get("authors")
        if authors_raw:
            author_details = [author["name"] for author in authors_raw]
        else:
            author_details = []
        
        venue_raw = candidate["_source"].get("venue")
        if venue_raw:
            venue = venue_raw.get("raw")
        else:
            venue = ""

        retrieved_art = Article(
            id=candidate["_id"],
            title=candidate["_source"].get("title"),
            url=candidate["_source"].get("url"),
            snippet=snippet,
            abstract=abstract, # candidate["_source"].get("document"),
            authors=", ".join(author_details),
            publication_date="publication_date",
            venue=venue
        )
        candidate_list.append(retrieved_art)

    return candidate_list
