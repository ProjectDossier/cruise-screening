import pandas as pd
import xmltodict
from fuzzywuzzy import fuzz

from .concept import Concept


class Taxonomy:
    def __init__(self):
        pass

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


class TaxonomyCCS(Taxonomy):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.taxonomy = self.read_taxonomy()
        print("Taxonomy instantiated")

    def read_taxonomy(self):
        with open(self.path, "r") as f:
            text = f.read()
            examples = xmltodict.parse(text)["rdf:RDF"]["skos:Concept"]

        id = "@rdf:about"
        name = "skos:prefLabel"
        childs = "skos:narrower"
        child = "@rdf:resource"
        example_list = []
        for example in examples:
            try:
                if len(example[childs]) == 1:
                    example[childs] = [example[childs]]
                for e_child in [i[child].split(".")[-1] for i in example[childs]]:
                    example_list.append(
                        [example[id].split(".")[-1], example[name]["#text"], e_child]
                    )
            except:
                example_list.append(
                    [example[id].split(".")[-1], example[name]["#text"], None]
                )

        table = pd.DataFrame(example_list, columns=["id", "text", "child"])
        table = table.drop_duplicates()
        table.text = table.text.str.lower()

        return table


class TaxonomyCSO(Taxonomy):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.taxonomy = self.read_taxonomy()
        print("Taxonomy instantiated")

    def read_taxonomy(self):
        df = pd.read_csv(self.path, header=None,
                         names=['item', 'relationship', 'item_rel'])

        # all the items are urls like '<url>' [:-1] removes '>'
        df = df.applymap(lambda x: x.split('/')[-1][:-1]).copy()
        # there's a constant substring 'cso#' not needed in relationships
        df.relationship = df.relationship.apply(lambda x: x.split('#')[-1])
        # labels and type might not be used. contributesTo not sure what it is yet
        # related links seem not well curated
        df = df[~df.relationship.isin(['label', 'type', 'contributesTo', 'relatedLink'])]
        # there are some strings with a segment after %
        # e.g, numerical_analysis % 2C_computer - assisted
        df = df.applymap(lambda x: x.split('%')[0])
        # names are give with '_'
        # e.g. automated_pattern_recognition
        df = df.applymap(lambda x: ' '.join(x.split('_')).lower().lstrip())
        # there are several relationships showing different ways of
        # writing/referring to the concept
        # relationships = ['relatedEquivalent',
        #                  'relatedEquivalent', 'preferentialEquivalent'
        #                  'sameAs', 'relatedLink']
        # trying to get same format adopted for ccs:
        taxonomy = df[df.relationship == 'supertopicof'].copy()
        # assign unique numbers to each concept
        text = set(list(taxonomy.item.values) + list(taxonomy.item_rel.values))
        ids = pd.DataFrame(list(text), columns=["text"]).reset_index()
        ids = ids.rename(columns={'index': 'id'})
        ids.id = ids.id.astype(str)
        # merge to replace concepts by ids
        taxonomy = taxonomy.merge(ids, left_on='item', right_on='text', how='outer')
        taxonomy.drop(columns=['item'], inplace=True)
        ids = ids.rename(columns={'id': 'child', 'text': 'item'})
        taxonomy = taxonomy.merge(ids, left_on='item_rel', right_on='item', how='left')
        taxonomy.drop(columns=['item', 'relationship', 'item_rel'], inplace=True)
        taxonomy = taxonomy.drop_duplicates()

        # careful! it seems like there are some parenting loops
        # 'search' method won't work
        return taxonomy
