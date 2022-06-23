from dataclasses import dataclass
from typing import List, Union, Dict


@dataclass
class Article:
    """Class for representing article from AMiner."""

    id: str
    title: str
    url: str
    snippet: str
    abstract: str
    authors: str
    publication_date: str = ""
    venue: str = ""
    keywords: list[str] = None
    keywords_snippet: Union[dict[str, Union[int, float]], None] = None
    keywords_rest: Union[dict[str, Union[int, float]], None] = None
    CSO_keywords: Union[dict[str, Union[int, float]], None] = None


@dataclass()
class WikipediaArticle:
    """Class for representing Wikipedia article."""

    id: str
    title: str
    url: str
    snippet: str
    content: str
    ambiguous: bool = True
    keywords: Union[List[str], None] = None
