import time

from concept_search.taxonomy import TaxonomyRDFCSO as Taxonomy
from django.shortcuts import render

from .search_documents import search
from .search_wikipedia import search_wikipedia
from .engine_logger import EngineLogger, get_query_type

engine_logger = EngineLogger()

# Create your views here.

# Taxonomy instantiation
taxonomy = Taxonomy()


def home(request):
    """
    Home page

    """
    if request.method == "GET":
        return render(
            request,
            "interfaces/home.html",
        )


def about(request):
    """
    About page
    """
    if request.method == "GET":
        return render(
            request,
            "interfaces/about.html",
        )


def search_results(request):
    """
    Search results page
    """
    if request.method == "GET":
        search_query = request.GET.get("search_query", None)
        query_type = get_query_type(
            search_button=request.GET.get("search_button", None)
        )

        if not search_query:
            return render(
                request,
                "interfaces/home.html",
            )
        s_time = time.time()

        index_name = "papers"
        top_k = 4
        search_result = search(query=search_query, index=index_name, top_k=top_k)
        concept_map = taxonomy.search(query=search_query)
        matched_wiki_page = search_wikipedia(query=search_query)
        search_time = time.time() - s_time

        engine_logger.log_query(
            search_query=search_query, query_type=query_type, search_time=search_time
        )

        context = {
            "search_result_list": search_result,
            "matched_wiki_page": matched_wiki_page,
            "unique_searches": len(search_result),
            "search_query": search_query,
            "concept_map": concept_map,
            "search_time": f"{search_time:.2f}",
        }

        return render(
            request=request,
            template_name="interfaces/search_result.html",
            context=context,
        )
