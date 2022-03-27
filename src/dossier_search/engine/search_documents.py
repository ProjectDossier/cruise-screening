import requests
import json
from utils.article import Article
import re


def highlighter(query: str, doc: str, es_highlighted_texts: list):
    pattern = re.compile(r'<em>(.*?)</em>')
    highlight_terms = []
    for line in es_highlighted_texts:
        highlight_terms += re.findall(pattern, line)

    highlighted_abstract = ""
    highlighted_snippet = ""
    for term in doc.split():
        if re.sub(r'[^\w]', '', term) in highlight_terms:
            term = '<em>' + term + '</em>'
        term += " "
        highlighted_abstract += term
        if len(highlighted_snippet) < 160:
            highlighted_snippet += term

    return highlighted_abstract[:-1], highlighted_snippet[:-1]


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
            abstract, snippet = highlighter(query, doc_text, candidate["highlight"]["document"])
        else:
            abstract = ""
            snippet = ""
        authors_raw = candidate["_source"].get("authors")
        if authors_raw:
            author_details = [author["name"] for author in authors_raw if "name" in author]
        else:
            author_details = []
        
        venue_raw = candidate["_source"].get("venue")
        if venue_raw:
            venue = venue_raw.get("raw")
        else:
            venue = ""

        url_candidates = candidate["_source"].get("url")
        url = ""
        if url_candidates:
            url = url_candidates[0]

        retrieved_art = Article(
            id=candidate["_id"],
            title=candidate["_source"].get("title"),
            url=url,
            snippet=snippet,
            abstract=abstract,  # candidate["_source"].get("document"),
            authors=", ".join(author_details),
            publication_date="publication_date",
            venue=venue,
            keywords_snippet=candidate["_source"].get("keywords")[:4],
            keywords_rest=candidate["_source"].get("keywords")[4:]
        )
        candidate_list.append(retrieved_art)

    return candidate_list
