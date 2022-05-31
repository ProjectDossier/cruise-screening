import logging
from typing import Optional


def get_query_type(source: Optional[str]) -> str:
    """
    Parse value of source GET param.
    Currently, if the person clicked search button it is filled with string "source".
    Otherwise, if the person clicked on taxonomy concept, it will be None.
    """
    if not source:
        return "other"
    else:
        return source


def get_wiki_logger(matched_wiki_page) -> str:
    if matched_wiki_page:
        return matched_wiki_page.url
    else:
        return "None"


class EngineLogger:
    """Simple wrapper for python logger to get a custom user query logger."""

    def __init__(self):
        self._logger = logging.getLogger("user_queries")
        hdlr = logging.FileHandler("../../data/user_queries.log")
        formatter = logging.Formatter("%(asctime)s %(message)s")
        hdlr.setFormatter(formatter)
        self._logger.addHandler(hdlr)
        self._logger.setLevel(logging.INFO)

    def log_query(self, search_query: str, query_type: str, search_time: float, tax_results:dict, matched_wiki_page:str):
        """Method responsible for logging user queries along with the search 'source'
        (either taxonomy concept or search box) and search time."""
        concepts = "\t".join(f"{k}: {v['concept']['text']}" for k, v in tax_results.items())
        self._logger.info(
            "\t%s\t%.4f\t%s\t%s\t%s", query_type, search_time, search_query, concepts, matched_wiki_page
        )

