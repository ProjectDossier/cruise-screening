from typing import List
from scholarly import scholarly

from utils.article import Article
from utils.article import Author
import re


def get_authors(names: List[str], scholar_ids: List[str] = None) -> List[Author]:
    _authors = []
    for index_i, _author_name in enumerate(names):
        scholar_id = None
        if scholar_ids:
            scholar_id = scholar_ids[index_i]
        _authors.append(Author(display_name=_author_name, google_scholar_id=scholar_id))

    return _authors


def revert_snippet(snippet):
    """snippet returned by scholarly contains double whitespaces both for newlines and
    for parts when google scholar merged two results. This method reverts this process by trying
    to find the double whitespace in the middle and replace it with one space char, and after replaces
    all other double spaces as elipsis."""
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


def search_google_scholar(query: str, index: str, top_k: int) -> List[Article]:
    pubs = scholarly.search_pubs(query, patents=False)

    candidate_list = []
    for index_i, candidate in enumerate(pubs):
        if index_i > top_k:
            break
        snippet = f"... {candidate['bib'].get('abstract')}"
        snippet = revert_snippet(snippet)
        abstract = None  # TODO: no easy way to get abstracts from google scholar

        _id = f"id_{hash(candidate['url_scholarbib'])}"  # no IDs in google scholar

        authors = get_authors(
            names=candidate["bib"].get("author"), scholar_ids=candidate.get("author_id")
        )
        authors = ", ".join([a.display_name for a in authors])
        publication_date = candidate["bib"].get("pub_year")
        try:
            publication_date = int(publication_date)
        except ValueError:
            publication_date = None


        retrieved_art = Article(
            id=_id,
            semantic_scholar_id=None,
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
            citations=candidate["num_citations"],
            references=None,
        )
        candidate_list.append(retrieved_art)

    return candidate_list
