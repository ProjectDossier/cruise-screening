from typing import Dict, Union

import wikipedia
from utils.article import WikipediaArticle


def search_wikipedia(query: str) -> Union[Dict[str, str], None]:
    """If there exist a wikipedia page with the title equal to the query it returns
    dictionary with the content of wikipedia page."""
    wikipedia.set_lang("en")
    try:
        page_object = wikipedia.page(query, auto_suggest=False)

        result = WikipediaArticle(
            id=page_object.pageid,
            title=page_object.title,
            url=page_object.url,
            snippet=f"{page_object.content[:300]}...",
            content=page_object.content,
        )
    except wikipedia.PageError:
        result = None
    except KeyError:
        result = None
    except wikipedia.DisambiguationError as e:
        page_object = wikipedia.page(e.options[0], auto_suggest=False)

        result = WikipediaArticle(
            id=page_object.pageid,
            title=page_object.title,
            url=page_object.url,
            snippet=f"{page_object.content[:300]}...",
            content=page_object.content,
            ambiguous=False,
        )

    return result
