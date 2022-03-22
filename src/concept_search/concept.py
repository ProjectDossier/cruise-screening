
class Concept:
    def __init__(self, id: str, text: str):
        self.id = id
        self.text = text
        self.parents = []
        self.children = []

    def set_parents(self, parents):
        self.parents = parents

    def set_children(self, children):
        self.children = children


def main(query):
    from src.concept_search.taxonomy import Taxonomy
    tax = Taxonomy('/data/external/acm_ccs.xml')

    id = tax.get_id(query)
    query = Concept(id, query)
    query.set_parents(tax.get_1st_level_parents(id))
    [item.set_parents(tax.get_1st_level_parents(item.id)) for item in query.parents]
    query.set_children(tax.get_1st_level_children(id))
    [item.set_children(tax.get_1st_level_children(item.id)) for item in query.children]
    return query


if __name__ == '__main__':
    main(query)
