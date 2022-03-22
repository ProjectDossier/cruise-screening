import wikipedia
from typing import Dict, Union


def search_wikipedia(query: str) -> Union[Dict[str, str], None]:
    """If there exist a wikipedia page with the title equal to the query it returns
    dictionary with the content of wikipedia page."""
    wikipedia.set_lang("en")
    try:
        page_object = wikipedia.page(query, auto_suggest=False)

        result = {
            "snippet": page_object.content[:500],
            "content": page_object.content,
            "url": page_object.url,
            "title": page_object.title,
            "id": page_object.pageid,
        }
    except wikipedia.PageError:
        result = None
    return result
