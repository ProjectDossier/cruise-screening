from typing import List, Union, Dict

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from utils.article import Article

Articles = List[Article]
SearchResultWithStatus = Dict[str, Union[Articles, int, str]]


def paginate_results(search_result: list, page: int, results_per_page: int = 19):
    paginator = Paginator(search_result, results_per_page)
    try:
        search_result_list = paginator.page(page)
    except PageNotAnInteger:
        search_result_list = paginator.page(1)
    except EmptyPage:
        search_result_list = paginator.page(paginator.num_pages)

    return search_result_list, paginator


def merge_results(
    internal_search_results: List[Article],
    core_search_results: List[Article],
    semantic_scholar_results: List[Article],
) -> List[Article]:
    output_results_dict = {
        item.title.lower().strip(): item for item in semantic_scholar_results
    }
    for _item in core_search_results:
        if _item.title.lower() not in output_results_dict.keys():
            semantic_scholar_results.append(_item)

    output_results_dict = {
        item.title.lower().strip(): item for item in semantic_scholar_results
    }
    for _item in internal_search_results:
        if _item.title.lower() not in output_results_dict.keys():
            semantic_scholar_results.append(_item)

    return semantic_scholar_results
