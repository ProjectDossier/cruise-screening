import time

from django.http import HttpResponseRedirect
from django.shortcuts import render
from concept_search.taxonomy import TaxonomyRDFCSO, TaxonomyRDFCCS
from concept_search.concept_rate import ConceptRate
from django.template.defaulttags import register

from .search_documents import search
from .search_wikipedia import search_wikipedia
from .engine_logger import EngineLogger, get_query_type

engine_logger = EngineLogger()

# Taxonomy instantiation
taxonomies = {
    "CSO": TaxonomyRDFCSO("../../data/external/"),
    "CCS": TaxonomyRDFCCS("../../data/external/"),
    "Wikipedia": TaxonomyRDFCCS("../../data/external/",
                                filename="wikipedia_taxonomy.xml",
                                taxonomy_name="wikipedia"),
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

        if not search_query.strip():
            return HttpResponseRedirect('index')

        s_time = time.time()

        index_name = "papers"
        top_k = 4
        search_result = search(query=search_query, index=index_name, top_k=top_k)
        ConceptRate().request_score(search_result=search_result)
        matched_wiki_page = search_wikipedia(query=search_query)
        search_time = time.time() - s_time

        engine_logger.log_query(
            search_query=search_query, query_type=query_type, search_time=search_time
        )

        tax_results = {}
        for name, taxonomy in taxonomies.items():
            concept = taxonomy.search(query=search_query)
            tax_results[name] = {
                "concept": concept.to_dict(),
                "subparents": [item.to_dict() for sublist in concept.parents for item in sublist.parents],
                "subchildren": [item.to_dict() for sublist in concept.children for item in sublist.children],
                "parents": [x.to_dict() for x in concept.parents],
                "children": [x.to_dict() for x in concept.children],
            }

        context = {
            "search_result_list": search_result,
            "matched_wiki_page": matched_wiki_page,
            "unique_searches": len(search_result),
            "search_time": f"{search_time:.2f}",
            "search_query": search_query,
            "tax_results": tax_results,
            "default_taxonomy": "CSO",
        }

        return render(
            request=request,
            template_name="interfaces/search_result.html",
            context=context,
        )
