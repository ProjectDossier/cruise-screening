import logging
import time

from concept_search.taxonomy import TaxonomyCCS as Taxonomy
from django.shortcuts import render

from .search_documents import search
from .search_wikipedia import search_wikipedia

logger = logging.getLogger("user_queries")
hdlr = logging.FileHandler("../../data/user_queries.log")
formatter = logging.Formatter("%(asctime)s %(message)s")
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


# Create your views here.

# Taxonomy instantiation
tax = Taxonomy("../../data/external/acm_ccs.xml")


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

        if not search_query:
            return render(
                request,
                "interfaces/home.html",
            )

        logger.info(search_query)
        s_time = time.time()

        index_name = "papers"
        top_k = 4
        search_result = search(query=search_query, index=index_name, top_k=top_k)
        tax_query = tax.search_relationships(query=search_query)
        matched_wiki_page = search_wikipedia(query=search_query)

        context = {
            "search_result_list": search_result,
            "matched_wiki_page": matched_wiki_page,
            "unique_searches": len(search_result),
            "search_query": search_query,
            "concept_map": tax_query,
            "search_time": f"{(time.time() - s_time):.2f}",
        }

        return render(
            request=request,
            template_name="interfaces/search_result.html",
            context=context,
        )
