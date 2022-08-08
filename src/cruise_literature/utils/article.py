from dataclasses import dataclass
from typing import Union, Optional


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
    fields_of_science: Optional[list[str]] = None
    keywords_snippet: Optional[dict[str, Union[int, float]]] = None
    keywords_rest: Optional[dict[str, Union[int, float]]] = None
    CSO_keywords: Optional[dict[str, Union[int, float]]] = None



@dataclass()
class WikipediaArticle:
    """Class for representing Wikipedia article."""

    id: str
    title: str
    url: str
    snippet: str
    content: str
    ambiguous: bool = True
    keywords: Optional[list[str]] = None


@dataclass()
class Author:
    """Class representing author."""

    id: str
    name: str
