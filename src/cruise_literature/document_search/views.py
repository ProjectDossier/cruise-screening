import concurrent.futures
import time

from concept_search.views import taxonomies
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.defaulttags import register

from .engine_logger import EngineLogger, get_query_type, get_wiki_logger
from .search_core import search_core
from .search_cruise import search_cruise
from .utils import paginate_results, merge_results
from .search_google_scholar import search_google_scholar
from .search_semantic_scholar import search_semantic_scholar
from .search_wikipedia import search_wikipedia
from .models import SearchEngine


engine_logger = EngineLogger()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def keywords_threshold(keyword_score):
    if keyword_score > 0.95:
        return "is-success"
    elif 0.7 < keyword_score <= 0.95:
        return "is-warning"
    elif 0 < keyword_score <= 0.7:
        return "is-danger"
    else:
        return ""


def search_results(request):
    """
    Search results page
    """
    if request.method == "GET":
        search_query = request.GET.get("search_query", None)
        query_type = get_query_type(source=request.GET.get("source", None))
        search_with_taxonomy = request.GET.get("search_type", False)

        if not search_query.strip():
            return HttpResponseRedirect("index")

        s_time = time.time()

        top_k = 50

        search_engines = SearchEngine.objects.filter(is_available=True).all()
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(search_engines)
        ) as executor:
            results = [
                executor.submit(eval(search_engine.search_method.split(".")[-1]), search_query, top_k)
                for search_engine in search_engines
            ]
            results = [
                future.result() for future in concurrent.futures.as_completed(results)
            ]
            search_result = merge_results(
                internal_search_results=results[0],
                core_search_results=results[1],
                semantic_scholar_results=results[2],
            )

        matched_wiki_page = search_wikipedia(query=search_query)
        search_time = time.time() - s_time

        search_result_list, paginator = paginate_results(
            search_result=search_result, page=request.GET.get("page", 1)
        )

        if not search_with_taxonomy and query_type in [
            "main_search",
            "reformulate_search",
        ]:
            # TODO: after document keyword click it will always use taxonomy
            engine_logger.log_query(
                search_query=search_query,
                query_type=query_type,
                search_time=search_time,
                tax_results={},
                matched_wiki_page=get_wiki_logger(matched_wiki_page),
            )

            context = {
                "search_result_list": search_result_list,
                "matched_wiki_page": matched_wiki_page,
                "unique_searches": len(search_result),
                "search_time": f"{search_time:.2f}",
                "search_query": search_query,
                "search_type": "",
                "paginator": paginator,
            }
            return render(
                request=request,
                template_name="interfaces/plain_search.html",
                context=context,
            )

        source_taxonomy = request.GET.get("source_taxonomy", None)
        if not source_taxonomy:
            source_taxonomy = list(taxonomies.keys())[0]

        engine_logger.log_query(
            search_query=search_query,
            query_type=query_type,
            search_time=search_time,
            tax_results={},
            matched_wiki_page=get_wiki_logger(matched_wiki_page),
        )

        context = {
            "search_result_list": search_result_list,
            "matched_wiki_page": matched_wiki_page,
            "unique_searches": len(search_result),
            "search_time": f"{search_time:.2f}",
            "search_query": search_query,
            "search_type": "checked",
            "default_taxonomy": source_taxonomy,
            "paginator": paginator,
        }
        # assign value of default taxonomy based on selected javascript box...
        return render(
            request=request,
            template_name="interfaces/search_with_taxonomy.html",
            context=context,
        )
