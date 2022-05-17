import time

from django.shortcuts import render
from concept_search.taxonomy import TaxonomyRDFCSO, TaxonomyRDFCCS
from django.template.defaulttags import register

from .search_documents import search
from .search_wikipedia import search_wikipedia
from .engine_logger import EngineLogger, get_query_type

engine_logger = EngineLogger()

# Create your views here.

# Taxonomy instantiation
taxonomies = {
    "CSO": TaxonomyRDFCSO("../../data/external/"),
    "CCS": TaxonomyRDFCCS("../../data/external/"),
}


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


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
        matched_wiki_page = search_wikipedia(query=search_query)
        search_time = time.time() - s_time

        engine_logger.log_query(
            search_query=search_query, query_type=query_type, search_time=search_time
        )

        tax_query = taxonomies["CSO"].search(query=search_query)
        tax_result = {
            "concept": tax_query,
            "parents": tax_query.parents,
            "subparents": list(
                set([item for sublist in tax_query.parents for item in sublist.parents])
            ),
            "children": tax_query.children,
            "subchildren": list(
                set(
                    [
                        item
                        for sublist in tax_query.children
                        for item in sublist.children
                    ]
                )
            ),
        }

        tax_results = {}
        for name, taxonomy in taxonomies.items():
            result = taxonomy.search(query=search_query)

            tax_results[name] = {
                "concept": result.to_json(),
                "subparents": [item.to_json() for sublist in result.parents for item in sublist.parents],
                "subchildren": [item.to_json() for sublist in result.children for item in sublist.children],
                "parents": [x.to_json() for x in result.parents],
                "children": [x.to_json() for x in result.children],
            }

        context = {
            "search_result_list": search_result,
            "matched_wiki_page": matched_wiki_page,
            "unique_searches": len(search_result),
            "search_query": search_query,
            "concept_map": tax_query,
            "search_time": f"{search_time:.2f}",
            "tax_result": tax_result,
            "tax_results": tax_results,
            "default_taxonomy": "CCS",
        }

        return render(
            request=request,
            template_name="interfaces/search_result.html",
            context=context,
        )
