from dataclasses import dataclass
from typing import Union, Optional, Dict, List


@dataclass
class Article:
    """Class for representing an article."""

    id: str
    title: str
    url: str  # this could be a list
    pdf: str
    snippet: str
    abstract: Optional[str]
    authors: str
    publication_date: str = ""
    publication_year: Optional[int] = None
    urls: Optional[List[str]] = None  # this could be a list
    venue: str = ""
    keywords_snippet: Union[Dict[str, Union[int, float]], None] = None
    keywords_rest: Union[Dict[str, Union[int, float]], None] = None
    CSO_keywords: Union[Dict[str, Union[int, float]], None] = None
    references: Optional[int] = None  # references count
    citations: Optional[int] = None  # citations count

    semantic_scholar_id: Optional[str] = None
    core_id: Optional[str] = None
    doi: Optional[str] = None
    pmid: Optional[str] = None
    arxiv_id: Optional[str] = None


@dataclass()
class WikipediaArticle:
    """Class for representing Wikipedia article."""

    id: str
    title: str
    url: str
    snippet: str
    content: str
    ambiguous: bool = True
    keywords: Optional[List[str]] = None


@dataclass()
class Author:
    """Class for representing an author."""

    display_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    id: Optional[str] = None
    aminer_id: Optional[str] = None
    semantic_scholar_id: Optional[str] = None
    google_scholar_id: Optional[str] = None
    orcid_id: Optional[str] = None
