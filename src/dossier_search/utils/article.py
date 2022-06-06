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
    keywords_snippet: Union[List[str], None] = None
    keywords_rest: Union[List[str], None] = None
    keywords_score: Dict = None

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
