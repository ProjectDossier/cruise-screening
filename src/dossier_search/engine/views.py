import time

from django.http import HttpResponseRedirect
from django.shortcuts import render
from concept_search.taxonomy import TaxonomyRDFCSO, TaxonomyRDFCCS
from concept_search.concept_rate import ConceptRate
from concept_search.concept_classification import CSOClassification
from django.template.defaulttags import register

from .search_documents import search, paginate_results
from .search_wikipedia import search_wikipedia
from .engine_logger import EngineLogger, get_query_type, get_wiki_logger

engine_logger = EngineLogger()

# Taxonomy instantiation
taxonomies = {
    "CSO": TaxonomyRDFCSO("../../data/external/"),
    "CCS": TaxonomyRDFCCS("../../data/external/"),
    "Wikipedia": TaxonomyRDFCCS(
        "../../data/external/",
        filename="wikipedia_taxonomy.xml",
        taxonomy_name="wikipedia",
    ),
}

concept_rate = ConceptRate().request_score
concept_clasifier = CSOClassification().classify_search_result

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def keywords_threshold(keyword_score):
    if keyword_score > 0.95:
        return 'is-success'
    elif 0.7 < keyword_score < 0.95:
        return 'is-warning'
    else:
        return 'is-danger'


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
        query_type = get_query_type(source=request.GET.get("source", None))
        search_with_taxonomy = request.GET.get("search_type", False)

        if not search_query.strip():
            return HttpResponseRedirect("index")

        s_time = time.time()

        index_name = "papers"
        top_k = 4
        search_result = search(query=search_query, index=index_name, top_k=top_k)

        search_result = concept_rate(search_result=search_result)
        search_result = concept_clasifier(search_result=search_result)
        for article in search_result:
            article.keywords_rest = article.keywords_rest + \
                                    list(set(article.CSO) - set(article.keywords_snippet + article.keywords_rest))

        matched_wiki_page = search_wikipedia(query=search_query)
        search_time = time.time() - s_time

        search_result_list, paginator = paginate_results(search_result=search_result, page = request.GET.get('page', 1))

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
                'paginator': paginator,
            }
            return render(
                request=request,
                template_name="interfaces/plain_search.html",
                context=context,
            )

        tax_results = {}
        for name, taxonomy in taxonomies.items():
            concept = taxonomy.search(query=search_query)
            tax_results[name] = {
                "concept": concept.to_dict(),
                "subparents": [
                    item.to_dict()
                    for sublist in concept.parents
                    for item in sublist.parents
                ],
                "subchildren": [
                    item.to_dict()
                    for sublist in concept.children
                    for item in sublist.children
                ],
                "parents": [x.to_dict() for x in concept.parents],
                "children": [x.to_dict() for x in concept.children],
            }

        source_taxonomy = request.GET.get("source_taxonomy", None)
        if not source_taxonomy:
            source_taxonomy = list(taxonomies.keys())[0]

        engine_logger.log_query(
            search_query=search_query,
            query_type=query_type,
            search_time=search_time,
            tax_results=tax_results,
            matched_wiki_page=get_wiki_logger(matched_wiki_page),
        )

        context = {
            "search_result_list": search_result_list,
            "matched_wiki_page": matched_wiki_page,
            "unique_searches": len(search_result),
            "search_time": f"{search_time:.2f}",
            "search_query": search_query,
            "tax_results": tax_results,
            "search_type": "checked",
            "default_taxonomy": source_taxonomy,
            'paginator': paginator,
        }
        # assign value of default taxonomy based on selected javascript box...
        return render(
            request=request,
            template_name="interfaces/search_with_taxonomy.html",
            context=context,
        )
