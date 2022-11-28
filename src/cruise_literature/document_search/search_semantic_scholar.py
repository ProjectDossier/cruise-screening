from typing import List, Dict
import requests
from utils.article import Article, Author

API_ENDPOINT = "https://api.semanticscholar.org/graph/v1/paper/search?query="

FIELDS = "externalIds,url,title,abstract,venue,year,referenceCount,citationCount,influentialCitationCount,isOpenAccess,\
fieldsOfStudy,s2FieldsOfStudy,publicationTypes,publicationDate,journal,authors"


def _get_authors(authors_list: List[Dict[str, str]]) -> List[Author]:
    return [
        Author(
            display_name=_author.get("name"),
            semantic_scholar_id=_author.get("authorId"),
        )
        for _author in authors_list
    ]


def search_semantic_scholar(query: str, top_k: int) -> List[Article]:
    response = requests.get(
        f"{API_ENDPOINT}{'+'.join(query.split())}&limit={top_k}&fields={FIELDS}"
    )

    candidate_list = []
    if response.status_code == 200:
        for index_i, candidate in enumerate(response.json()["data"]):
            try:
                snippet = candidate.get("abstract")[:300]
                abstract = candidate.get("abstract")
            except TypeError:
                snippet = ""
                abstract = ""

            if candidate.get("externalIds").get("ArXiv"):
                pdf = f"https://arxiv.org/pdf/{candidate.get('externalIds').get('ArXiv')}.pdf"
            else:
                pdf = None

            doi = candidate.get("externalIds").get("DOI") or None
            authors = _get_authors(candidate.get("authors"))
            authors = ", ".join([a.display_name for a in authors])
            year = date[:4] if (date := candidate["publicationDate"]) else "   "
            retrieved_art = Article(
                id=candidate["paperId"],
                semantic_scholar_id=candidate["paperId"],
                core_id=None,
                doi=doi,
                title=candidate.get("title"),
                url=candidate["url"],
                pdf=pdf,
                snippet=snippet,
                abstract=abstract,
                authors=authors,
                publication_date=year,
                venue=candidate["venue"],
                keywords_snippet=None,
                keywords_rest=None,
                CSO_keywords=None,
                citations=candidate.get("citationCount"),
                references=candidate.get("referenceCount"),
            )
            candidate_list.append(retrieved_art)

    return candidate_list
