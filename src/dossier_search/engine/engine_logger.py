import logging
from typing import Optional


def get_query_type(search_button: Optional[str]) -> str:
    """
    Parse value of search_button GET param.
    Currently, if the person clicked search button it is filled with string "search_button".
    Otherwise (if the person clicked on taxonomy concept), it will be None.
    """
    if not search_button:
        return "taxonomy"
    elif search_button == "search_button":
        return "query_box"
    else:
        return "other"


class EngineLogger:
    """Simple wrapper for python logger to get a custom user query logger."""

    def __init__(self):
        self._logger = logging.getLogger("user_queries")
        hdlr = logging.FileHandler("../../data/user_queries.log")
        formatter = logging.Formatter("%(asctime)s %(message)s")
        hdlr.setFormatter(formatter)
        self._logger.addHandler(hdlr)
        self._logger.setLevel(logging.INFO)

    def log_query(self, search_query: str, query_type: str, search_time: float):
        """Method responsible for logging user queries along with the search 'source'
        (either taxonomy concept or search box) and search time."""
        self._logger.info(
            "type: %s\ttime %.4f\tquery: %s", query_type, search_time, search_query
        )
