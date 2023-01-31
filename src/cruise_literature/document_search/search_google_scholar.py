from typing import List

import fake_useragent

try:
    from scholarly import scholarly
except fake_useragent.errors.FakeUserAgentError:
    scholarly = None

from document_search.utils import SearchResultWithStatus
from utils.article import Article, generate_uuid
from utils.article import Author
import re


def _get_authors(names: List[str], scholar_ids: List[str] = None) -> List[Author]:
    _authors = []
    for index_i, _author_name in enumerate(names):
        scholar_id = None
        if scholar_ids:
            scholar_id = scholar_ids[index_i]
        _authors.append(Author(display_name=_author_name, google_scholar_id=scholar_id))

    return _authors


def revert_snippet(snippet: str) -> str:
    """snippet returned by scholarly contains double whitespaces both for newlines and
    for parts when Google Scholar merged two results. This method reverts this process by trying
    to find the double whitespace in the middle and replace it with one space char, and after replaces
    all other double spaces as ellipsis."""
    lower_bound = len(snippet) // 2 - 5
    upper_bound = len(snippet) // 2 + 5
    new_snippet = next(
        (
            f"{snippet[:newline_candidate.span()[0]]} {snippet[newline_candidate.span()[1]:]}"
            for newline_candidate in re.finditer("  ", snippet)
            if lower_bound < newline_candidate.span()[0] < upper_bound
        ),
        "",
    )

    new_snippet = re.sub("  ", " ... ", new_snippet)
    return new_snippet


def search_google_scholar(query: str, top_k: int) -> SearchResultWithStatus:
    if scholarly is None:
        return {
            "results": [],
            "status": "ERROR",
            "status_code": 503,
            "search_engine": "Google Scholar",
            "search_query": query,
        }

    pubs = scholarly.search_pubs(query, patents=False)

    candidate_list = []
    for index_i, candidate in enumerate(pubs):
        if index_i > top_k:
            break
        snippet = f"... {candidate['bib'].get('abstract')}"
        snippet = revert_snippet(snippet)
        abstract = None  # TODO: no easy way to get abstracts from google scholar

        _id = f"id_{hash(candidate['url_scholarbib'])}"  # no IDs in google scholar

        authors = _get_authors(
            names=candidate["bib"].get("author"), scholar_ids=candidate.get("author_id")
        )
        authors = ", ".join([a.display_name for a in authors])
        publication_date = candidate["bib"].get("pub_year")
        try:
            publication_date = int(publication_date)
        except ValueError:
            publication_date = None

        uuid = generate_uuid()
        retrieved_art = Article(
            id=uuid,
            google_scholar_hash_id=_id,
            core_id=None,
            title=candidate["bib"].get("title"),
            url=candidate.get("pub_url"),
            pdf=candidate.get("eprint_url"),
            snippet=snippet,
            abstract=abstract,
            authors=authors,
            publication_date=publication_date,
            venue=candidate["bib"].get("venue"),
            keywords_snippet=None,
            keywords_rest=None,
            CSO_keywords=None,
            n_citations=candidate["num_citations"],
            n_references=None,
        )
        candidate_list.append(retrieved_art)

    if candidate_list:
        _status = "OK"
        _status_code = 200
    else:
        _status = "ERROR"
        _status_code = 503

    return {
        "results": candidate_list,
        "status": _status,
        "status_code": _status_code,
        "search_engine": "Google Scholar",
        "search_query": query,
    }
