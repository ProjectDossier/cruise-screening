from typing import List, Dict

import requests
import os
from cruise_literature.settings import SEARCH_WITH_CORE
from document_search.utils import SearchResultWithStatus

from utils.article import Article

from utils.article import Author

if SEARCH_WITH_CORE:
    CURRENT_FILE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
    api_key_file = f"{CURRENT_FILE_DIRECTORY}/../../../data/core_api_key.txt"

    with open(api_key_file, "r") as apikey_file:
        api_key = apikey_file.readlines()[0].strip()
        if api_key == "ADD_YOUR_CORE_API_KEY_HERE":
            raise ValueError(
                f"You need to update CORE API key in {api_key_file} in order to use CORE search"
            )

api_endpoint = "https://api.core.ac.uk/v3/search/works"


def _get_authors(authors_list: List[Dict[str, str]]) -> List[Author]:
    return [
        Author(
            display_name=_author.get("name"),
        )
        for _author in authors_list
    ]


def search_core(query: str, top_k: int) -> SearchResultWithStatus:
    if not SEARCH_WITH_CORE:
        return {
            "results": [],
            "status": "ERROR",
            "status_code": 501,
            "search_engine": "CORE",
            "search_query": query,
        }
    data = {
        "q": query,
        "limit": str(top_k),
    }
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    response = requests.post(url=api_endpoint, headers=headers, json=data)
    candidate_list = []
    if response.status_code == 200:
        for index_i, candidate in enumerate(response.json()["results"]):

            try:
                snippet = candidate.get("abstract")[:300]
                abstract = candidate.get("abstract")
            except TypeError:
                snippet = ""
                abstract = ""

            authors = _get_authors(candidate.get("authors"))
            authors = ", ".join([a.display_name for a in authors])

            year = candidate.get("yearPublished")
            if not year:
                year = "   "

            urls = candidate.get("links")
            if urls and len(urls) >= 4:
                url = urls[4]["url"]
            elif urls and len(urls) >= 2:
                url = urls[1]["url"]
            elif urls:
                url = urls[0]["url"]
            else:
                url = None

            doi = candidate.get("doi")
            citations_count = candidate.get("citationCount")
            if not citations_count:
                citations_count = 0

            title = candidate.get("title")
            if not title:
                title = ""

            retrieved_art = Article(
                id=candidate["id"],
                semantic_scholar_id=None,
                core_id=candidate["id"],
                doi=doi,
                title=title,
                url=url,
                pdf=candidate.get("downloadUrl"),
                snippet=snippet,
                abstract=abstract,
                authors=authors,
                publication_date=year,
                venue=candidate.get("publisher"),
                keywords_snippet=None,
                keywords_rest=None,
                CSO_keywords=None,
                n_citations=citations_count,
                n_references=len(candidate.get("references")),
            )
            candidate_list.append(retrieved_art)

    _status = "OK" if response.status_code == 200 else "ERROR"
    return {
        "results": candidate_list,
        "status": _status,
        "status_code": response.status_code,
        "search_engine": "CORE",
        "search_query": query,
    }
