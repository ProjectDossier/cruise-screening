from django.http import JsonResponse

from .taxonomy import TaxonomyRDFCSO, TaxonomyRDFCCS

taxonomies = {
    "CSO": TaxonomyRDFCSO("../../data/external/"),
    "CCS": TaxonomyRDFCCS("../../data/external/"),
    "Wikipedia": TaxonomyRDFCCS(
        "../../data/external/",
        filename="wikipedia_taxonomy.xml",
        taxonomy_name="wikipedia",
    ),
}


def search_concepts(request, query):
    """
    Search concepts relevant to the query inside taxonomies
    """
    if request.method == "GET":
        tax_results = []
        for name, taxonomy in taxonomies.items():
            concept = taxonomy.search(query=query)
            tax_results.append({
                "name": name,
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
            )

        return JsonResponse(tax_results, safe=False)
