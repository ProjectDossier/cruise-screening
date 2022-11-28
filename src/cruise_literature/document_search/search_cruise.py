import json
import re
from typing import List

import requests
from utils.article import Article


def highlighter(doc: str, es_highlighted_texts: List[str]):
    pattern = re.compile(r"<em>(.*?)</em>")
    highlight_terms = []
    for line in es_highlighted_texts:
        highlight_terms += re.findall(pattern, line)

    highlighted_abstract = ""
    highlighted_snippet = ""
    for term in doc.split():
        if re.sub(r"[^\w]", "", term) in highlight_terms:
            term = "<em>" + term + "</em>"
        term += " "
        highlighted_abstract += term
        if len(highlighted_snippet) < 160:
            highlighted_snippet += term

    return highlighted_abstract[:-1], highlighted_snippet[:-1]


def search_cruise(query: str, top_k: int) -> List[Article]:
    """Search internal elasticsearch database."""
    index_name = "papers"
    headers = {"Content-type": "application/json"}
    res = requests.post(
        "http://localhost:9880" + "/search",
        data=json.dumps({"query": query, "es_index": index_name, "es_top_k": top_k}),
        headers=headers,
    )
    results = res.json()["results"]
    candidate_list = []
    for candidate in results["hits"]["hits"]:
        doc_text = candidate["_source"].get("abstract")
        if doc_text and "abstract" in candidate["highlight"]:
            abstract, snippet = highlighter(
                doc_text, candidate["highlight"]["abstract"]
            )
        else:
            abstract = candidate["_source"].get("abstract")
            snippet = candidate["_source"].get("abstract")[:300]

        authors_raw = candidate["_source"].get("authors")
        if authors_raw:
            author_details = [
                author["name"] for author in authors_raw if "name" in author
            ]
        else:
            author_details = []

        citations = len(candidate["_source"].get("n_citations"))
        if citations == 0:  # TODO: learn why citation is equal to 0
            citations = "-"
        references = len(candidate["_source"].get("references"))

        venue_raw = candidate["_source"].get("venue")
        if venue_raw and venue_raw.get("name_d"):
            venue = venue_raw.get("name_d")
        elif venue_raw and venue_raw.get("raw"):
            venue = venue_raw.get("raw")
        else:
            venue = ""

        pdf = candidate["_source"].get("pdf")
        doi = candidate["_source"].get("doi")

        url_candidates = candidate["_source"].get("url")
        url = ""
        if url_candidates:
            url = url_candidates[0]

        keywords_snippet = {}
        keywords_rest = {}
        index_i = 0
        for k, v in sorted(
            candidate["_source"].get("keywords").items(),
            key=lambda item: item[1],
            reverse=True,
        ):
            index_i += 1
            if index_i < 5:
                keywords_snippet[k] = v
            else:
                keywords_rest[k] = v

        retrieved_art = Article(
            id=candidate["_id"],
            title=candidate["_source"].get("title"),
            url=url,
            pdf=pdf,
            snippet=snippet,
            abstract=abstract,
            authors=", ".join(author_details),
            publication_date=candidate["_source"].get("year"),
            venue=venue,
            keywords_snippet=keywords_snippet,
            keywords_rest=keywords_rest,
            CSO_keywords=candidate["_source"].get("CSO_keywords")["union"],
            citations=citations,
            references=references,
            doi=doi,
        )
        candidate_list.append(retrieved_art)

    return candidate_list


