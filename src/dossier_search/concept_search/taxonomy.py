from abc import ABC, abstractmethod
import pandas as pd
import xmltodict
from fuzzywuzzy import fuzz
from .faiss_search import SemanticSearch
from .lexical_search import LexicalSearch

from .concept import Concept


class Taxonomy(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def read_taxonomy(self):
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
            if id == -100:
                try:
                    query_ = self.lexical_search(query)
                    id = taxonomy[taxonomy.text == query_].id.values[0]
                except: pass
            if id == -100:
                try:
                    query, _ = self.semantic_search(query)
                    id = taxonomy[taxonomy.text == query].id.values[0]
                except: pass

        return id, query

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
        id, query = self.get_id(query)
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
        self.taxonomy, concept_list = self.read_taxonomy()
        self.semantic_search = SemanticSearch(data=concept_list, tax_name="CCS").do_faiss_lookup
        self.lexical_search = LexicalSearch(data=self.concept_list, tax_name="CCS").lexical_search

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
        table.sort_values('text', inplace=True)
        concept_list = list(table.text.unique())
        concept_list.sort()

        return table, concept_list


class TaxonomyCSO(Taxonomy):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.taxonomy, self.concept_list = self.read_taxonomy()
        self.semantic_search = SemanticSearch(data=self.concept_list, tax_name="CSO").do_faiss_lookup
        self.lexical_search = LexicalSearch(data=self.concept_list, tax_name="CSO").lexical_search
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
        df = df[~df.relationship.isin(['label', 'type', 'relatedLink'])]
        # there are some strings with a segment after %
        # e.g, numerical_analysis % 2C_computer - assisted
        df = df.applymap(lambda x: x.split('%')[0])
        # names are given with '_'
        # e.g. automated_pattern_recognition
        df = df.applymap(lambda x: ' '.join(x.split('_')).lower().lstrip())
        # names are given with '-'
        # e.g. context-aware systems
        df = df.applymap(lambda x: ' '.join(x.split('-')).lower().lstrip())
        # there are several relationships showing different ways of
        # writing/referring to the concept
        # relationships = ['relatedequivalent', 'preferentialequivalent',
        #                  'sameas', 'contributesto']
        df_temp = df[df.item != df.item_rel].copy()
        unique_concepts = list(df_temp[df_temp.relationship == 'preferentialequivalent'].item)
        unique_concepts += set(df.item) - set(df[df.relationship.isin(['preferentialequivalent'])].item)
        redundant_concepts = set(df.item) - set(unique_concepts)
        df = df[df.item.isin(unique_concepts) & (~df.item_rel.isin(redundant_concepts))].copy()
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
        taxonomy = taxonomy[~(taxonomy.text == '')]
        # required to match index
        taxonomy.sort_values('text', inplace=True)
        concept_list = list(taxonomy.text.unique())
        concept_list.sort()
        return taxonomy, concept_list
