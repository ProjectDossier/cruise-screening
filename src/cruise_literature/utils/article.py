from dataclasses import dataclass
from typing import Union, Optional, Dict, List


@dataclass
class Article:
    """Class for representing article from AMiner."""

    id: str
    title: str
    url: str
    pdf: str
    snippet: str
    abstract: str
    authors: str
    publication_date: str = ""
    venue: str = ""
    keywords_snippet: Union[Dict[str, Union[int, float]], None] = None
    keywords_rest: Union[Dict[str, Union[int, float]], None] = None
    CSO_keywords: Union[Dict[str, Union[int, float]], None] = None
    references: Optional[int] = None  # references count
    citations: Optional[int] = None  # citations count


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
    """Class representing author."""

    display_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    id: Optional[str] = None
    aminer_id: Optional[str] = None
    semantic_scholar_id: Optional[str] = None
