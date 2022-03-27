import pandas as pd
import xmltodict
from fuzzywuzzy import fuzz

from .concept import Concept


class Taxonomy:
    def __init__(self, path):
        self.path = path
        self.taxonomy = self.get_ccs(path)

        print("Taxonomy instantiated")

    def get_ccs(self, path):
        with open(path, "r") as f:
            text = f.read()
            examples = xmltodict.parse(text)['rdf:RDF']['skos:Concept']

        id = '@rdf:about'
        name = 'skos:prefLabel'
        childs = 'skos:narrower'
        child = '@rdf:resource'
        example_list = []
        for example in examples:
            try:
                if len(example[childs]) == 1:
                    example[childs] = [example[childs]]
                for e_child in [i[child].split('.')[-1] for i in example[childs]]:
                    example_list.append([example[id].split('.')[-1],
                                         example[name]['#text'],
                                         e_child])
            except:
                example_list.append([example[id].split('.')[-1], example[name]['#text'], None])

        table = pd.DataFrame(example_list, columns=["id", "text", "child"])
        table = table.drop_duplicates()
        table.text = table.text.str.lower()

        return table

    def get_id(self, query: str) -> str:
        query = query.lower().lstrip()
        taxonomy = self.taxonomy
        try:
            id = taxonomy[taxonomy.text == query].id.values[0]
        except:
            scores = taxonomy.text.apply(lambda x: fuzz.ratio(x, query))
            max_value, idx = scores.max(), scores.idxmax()
            # -100 is the id we use when the query is not found in the taxonomy
            id = taxonomy.iloc[idx].id if max_value > 90 else -100
        return id

    def get_1st_level_parents(self, id):
        taxonomy = self.taxonomy
        parents = taxonomy[taxonomy.child == id][["id", "text"]].values
        return [Concept(item[0], item[1]) for item in parents]

    def get_1st_level_children(self, id):
        taxonomy = self.taxonomy
        children = list(taxonomy[taxonomy.id == id].child)
        children = taxonomy[taxonomy.id.isin(children)][["id", "text"]]
        children = children.drop_duplicates().values
        return [Concept(item[0], item[1]) for item in children]

    def assign_parents(self, item):
        parent = Concept(item[0], item[1])
        parent.parents = self.get_parents(id=item[0])
        return parent

    def get_parents(self, id):
        taxonomy = self.taxonomy
        parents = taxonomy[taxonomy.child == id][["id", "text"]].values
        return [self.assign_parents(item) for item in parents]

    def assign_children(self, item):
        child = Concept(item[0], item[1])
        child.children = self.get_children(item[0])
        return child

    def get_children(self, id):
        taxonomy = self.taxonomy
        children = list(taxonomy[taxonomy.id == id].child)
        children = taxonomy[taxonomy.id.isin(children)][["id", "text"]]
        children = children.drop_duplicates().values
        return [self.assign_children(item) for item in children]

    def search_relationships(self, query):
        id = self.get_id(query)
        if id == -100:
            return Concept(-100, query)
        query = Concept(id, query)
        query.parents = self.get_1st_level_parents(id)
        for item in query.parents:
            item.parents = self.get_1st_level_parents(item.id)
        query.children = self.get_1st_level_children(id)
        for item in query.children:
            item.children = self.get_1st_level_children(item.id)
        return query

    def search(self, query):
        id = self.get_id(query)
        if id == -100:
            return Concept(-100, query)
        query = Concept(id, query)
        query.parents = self.get_parents(id)
        query.children = self.get_children(id)
        return query
