from dataclasses import dataclass


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


@dataclass()
class WikipediaArticle:
    """Class for representing Wikipedia article."""
    id: str
    title: str
    url: str
    snippet: str
    content: str
    ambiguous: bool = True
