from abc import ABC, abstractmethod
from os.path import join as path_join
from typing import Tuple

import pandas as pd
import xmltodict
from dossier_search.settings import M1_CHIP
from fuzzywuzzy import fuzz
from rdflib import Graph, Namespace

from .concept import Concept
from .faiss_search import SemanticSearch

if M1_CHIP:

    class LexicalSearch:
        """Mockup for LexicalSearch on laptops with M1 chip.
        FIXME: this should be replaced at some point by a different implementation
        of lexical search.
        """

        def __init__(self, data, tax_name):
            pass

        def lexical_search(self, query):
            raise IndexError

else:
    from .lexical_search import LexicalSearch


class Taxonomy(ABC):
    taxonomy = None
    MAX_DEPTH = 2

    def __init__(self):
        pass

    @abstractmethod
    def read_taxonomy(self):
        pass

    def get_id(self, query: str) -> Tuple[int, str]:
        query = query.lower().lstrip()
        taxonomy = self.taxonomy
        try:
            id = taxonomy[taxonomy.text == query].id.values[0]
        except IndexError:
            scores = taxonomy.text.apply(lambda x: fuzz.ratio(x, query))
            max_value, idx = scores.max(), scores.idxmax()
            # -100 is the id we use when the query is not found in the taxonomy
            id = taxonomy.iloc[idx].id if max_value > 90 else -100
            if id == -100:
                try:
                    query_ = self.lexical_search(query)
                    id = taxonomy[taxonomy.text == query_].id.values[0]
                except IndexError:
                    query, _ = self.semantic_search(query)
                    id = taxonomy[taxonomy.text == query].id.values[0]
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

    def assign_parents(self, item, depth: int):
        parent = Concept(item[0], item[1])
        if depth == self.MAX_DEPTH:
            return parent
        parent.parents = self.get_parents(id=item[0], depth=depth)
        parent.parent_ids = "-".join([item.id for item in parent.parents])
        return parent

    def get_parents(self, id, depth: int):
        depth += 1
        taxonomy = self.taxonomy
        parents = taxonomy[taxonomy.child == id][["id", "text"]].values
        return [self.assign_parents(item, depth=depth) for item in parents]

    def assign_children(self, item, depth: int):
        child = Concept(item[0], item[1])
        if depth == self.MAX_DEPTH:
            return child
        child.children = self.get_children(item[0], depth=depth)
        child.children_ids = "-".join([child_.id for child_ in child.children])
        return child

    def get_children(self, id, depth: int):
        depth += 1
        taxonomy = self.taxonomy
        children = list(taxonomy[taxonomy.id == id].child)
        children = taxonomy[taxonomy.id.isin(children)][["id", "text"]]
        children = children.drop_duplicates().values
        return [self.assign_children(item, depth=depth) for item in children]

    def search_relationships(self, query):
        id, query = self.get_id(query)
        if id == -100:
            return Concept(-100, query)
        query = Concept(id, query)
        query.parents = self.get_1st_level_parents(id)
        for item in query.parents:
            item.parents = self.get_1st_level_parents(item.id)
            item.children_ids = "-".join([child_.id for child_ in item.children])
        query.children = self.get_1st_level_children(id)
        for item in query.children:
            item.children = self.get_1st_level_children(item.id)
        return query

    def search(self, query, to_json=False):
        id = self.get_id(query)
        if id == -100:
            query = Concept(-100, query)
            if to_json:
                return {
                "concept": query.to_dict(),
                "subparents": [],
                "subchildren": [],
                "parents": [],
                "children": [],
                }
            else:
                return query
        query = Concept(id, query)

        depth = 0

        query.parents = self.get_parents(id, depth=depth)
        query.children = self.get_children(id, depth=depth)
        query.children_ids = "-".join([item.id for item in query.children])
        query.parent_ids = "-".join([item.id for item in query.parents])

        if to_json:
            subparents = list(set([item for sublist in query.parents for item in sublist.parents]))
            subchildren = list(set([item for sublist in query.children for item in sublist.children]))
            return {
                "concept": query.to_dict(),
                "subparents": [item.to_dict() for item in subparents],
                "subchildren": [item.to_dict() for item in subchildren],
                "parents": [x.to_dict() for x in query.parents],
                "children": [x.to_dict() for x in query.children],
            }
        return query


class TaxonomyCCS(Taxonomy):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.taxonomy, self.concept_list = self.read_taxonomy()
        self.semantic_search = SemanticSearch(
            data=self.concept_list, tax_name="CCS"
        ).do_faiss_lookup
        self.lexical_search = LexicalSearch(
            data=self.concept_list, tax_name="CCS"
        ).lexical_search

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
        table.sort_values("text", inplace=True)
        concept_list = list(table.text.unique())
        concept_list.sort()

        return table, concept_list


class TaxonomyCSO(Taxonomy):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.taxonomy, self.concept_list = self.read_taxonomy()
        self.semantic_search = SemanticSearch(
            data=self.concept_list, tax_name="CSO"
        ).do_faiss_lookup
        self.lexical_search = LexicalSearch(
            data=self.concept_list, tax_name="CSO"
        ).lexical_search
        print("Taxonomy instantiated")

    def read_taxonomy(self):
        df = pd.read_csv(
            self.path, header=None, names=["item", "relationship", "item_rel"]
        )

        # all the items are urls like '<url>' [:-1] removes '>'
        df = df.applymap(lambda x: x.split("/")[-1][:-1]).copy()
        # there's a constant substring 'cso#' not needed in relationships
        df.relationship = df.relationship.apply(lambda x: x.split("#")[-1])
        # labels and type might not be used. contributesTo not sure what it is yet
        # related links seem not well curated
        df = df[~df.relationship.isin(["label", "type", "relatedLink"])]
        # there are some strings with a segment after %
        # e.g, numerical_analysis % 2C_computer - assisted
        df = df.applymap(lambda x: x.split("%")[0])
        # names are given with '_'
        # e.g. automated_pattern_recognition
        df = df.applymap(lambda x: " ".join(x.split("_")).lower().lstrip())
        # names are given with '-'
        # e.g. context-aware systems
        df = df.applymap(lambda x: " ".join(x.split("-")).lower().lstrip())
        # there are several relationships showing different ways of
        # writing/referring to the concept
        # relationships = ['relatedequivalent', 'preferentialequivalent',
        #                  'sameas', 'contributesto']
        df_temp = df[df.item != df.item_rel].copy()
        unique_concepts = list(
            df_temp[df_temp.relationship == "preferentialequivalent"].item
        )
        unique_concepts += set(df.item) - set(
            df[df.relationship.isin(["preferentialequivalent"])].item
        )
        redundant_concepts = set(df.item) - set(unique_concepts)
        df = df[
            df.item.isin(unique_concepts) & (~df.item_rel.isin(redundant_concepts))
        ].copy()
        taxonomy = df[df.relationship == "supertopicof"].copy()
        # assign unique numbers to each concept
        text = set(list(taxonomy.item.values) + list(taxonomy.item_rel.values))
        ids = pd.DataFrame(list(text), columns=["text"]).reset_index()
        ids = ids.rename(columns={"index": "id"})
        ids.id = ids.id.astype(str)
        # merge to replace concepts by ids
        taxonomy = taxonomy.merge(ids, left_on="item", right_on="text", how="outer")
        taxonomy.drop(columns=["item"], inplace=True)
        ids = ids.rename(columns={"id": "child", "text": "item"})
        taxonomy = taxonomy.merge(ids, left_on="item_rel", right_on="item", how="left")
        taxonomy.drop(columns=["item", "relationship", "item_rel"], inplace=True)
        taxonomy = taxonomy.drop_duplicates()
        taxonomy = taxonomy[~(taxonomy.text == "")]
        # required to match index
        taxonomy.sort_values("text", inplace=True)
        concept_list = list(taxonomy.text.unique())
        concept_list.sort()
        return taxonomy, concept_list


class TaxonomyRDF(Taxonomy):
    def __init__(self):
        super().__init__()
        self.namespace = None
        self.rdf_query_parents = None
        self.rdf_query_children = None
        self.graph = None
        self.MAX_DEPTH = 2
        self.path = "../../data/external"

    @abstractmethod
    def read_taxonomy(self):
        pass

    def format_taxonomy(self, graph, query):
        res = graph.query(query)

        df = pd.DataFrame(
            [
                (
                    x["x"].n3(graph.namespace_manager),
                    x["z"].n3(graph.namespace_manager)[1:-4],
                )
                for x in res
            ],
            columns=["node", "text"],
        )

        df.node = df.node.apply(lambda x: x[1:-1])
        # names are given with '-'
        # e.g. context-aware systems
        df.text = df.text.apply(lambda x: x.lower().lstrip())
        df.text = df.text.apply(lambda x: " ".join(x.split("-")))
        df.rename(columns={"node": "id"}, inplace=True)
        df = df[~(df.text == "")]
        df = df.reset_index(drop=True)

        df.sort_values("text", inplace=True)
        concept_list = list(df.text.unique())
        concept_list.sort()

        return df, concept_list

    def assign_children(self, node, text, depth):
        child = Concept(node, text)
        if depth == self.MAX_DEPTH:
            return child
        child.children = self.get_children(child, depth)
        return child

    def get_children(self, query, depth):
        depth += 1
        rdf_query = self.rdf_query_children % {"node": query.id}
        res = self.graph.query(rdf_query)
        return [
            self.assign_children(
                i["x"], i["z"].n3(self.graph.namespace_manager)[1:-4], depth
            )
            for i in res
        ]

    def assign_parents(self, node, text, depth):
        parent = Concept(node, text)
        if depth == self.MAX_DEPTH:
            return parent
        parent.parents = self.get_parents(parent, depth)
        return parent

    def get_parents(self, query, depth):
        depth += 1
        rdf_query = self.rdf_query_parents % {"node": query.id}
        res = self.graph.query(rdf_query)
        return [
            self.assign_parents(
                i["x"], i["z"].n3(self.graph.namespace_manager)[1:-4], depth
            )
            for i in res
        ]

    def search(self, query):
        node, query = self.get_id(query)
        if id == -100:
            return Concept(-100, query)
        query = Concept(self.namespace[node], query)
        query.children, query.parents = (
            self.get_children(query, depth=0),
            self.get_parents(query, depth=0),
        )
        return query


class TaxonomyRDFCSO(TaxonomyRDF):
    def __init__(self, path=None):
        super().__init__()
        if path is not None:
            self.path = path
        (
            self.graph,
            self.namespace,
            self.taxonomy,
            self.concept_list,
        ) = self.read_taxonomy()
        self.semantic_search = SemanticSearch(
            data=self.concept_list, tax_name="CSO_RDF"
        ).do_faiss_lookup
        self.lexical_search = LexicalSearch(
            data=self.concept_list, tax_name="CSO_RDF"
        ).lexical_search

        self.rdf_query_children = f"""
                            select ?x ?z where
                            {{
                                {{
                                    {{
                                        ?x ns0:preferentialEquivalent ?x .
                                    }}
                                    {{
                                        select * where
                                        {{
                                            <%(node)s> ns0:superTopicOf ?x . ?x ns1:label ?z .
                                        }}
                                    }}
                                }}
                                UNION
                                {{
                                    select * where
                                    {{
                                        <%(node)s> ns0:superTopicOf ?x . ?x ns1:label ?z
                                        FILTER (!EXISTS
                                        {{
                                            ?x ns0:preferentialEquivalent ?y
                                        }})
                                    }}
                                }}
                            }}
                        """
        self.rdf_query_parents = f"""
                            select ?x ?z where
                            {{
                                {{
                                    {{
                                        ?x ns0:preferentialEquivalent ?x .
                                    }}
                                    {{
                                        select * where
                                        {{
                                            ?x ns0:superTopicOf <%(node)s> . ?x ns1:label ?z .
                                        }}
                                    }}
                                }}
                                UNION
                                {{
                                    select * where
                                    {{
                                        ?x ns0:superTopicOf <%(node)s> . ?x ns1:label ?z
                                        FILTER (!EXISTS
                                        {{
                                            ?x ns0:preferentialEquivalent ?y
                                        }})
                                    }}
                                }}
                            }}
                        """
        print("Taxonomy instantiated")

    def read_taxonomy(self):
        namespace = Namespace("")
        graph = Graph().parse(path_join(self.path, "CSO.3.3.ttl"), format="ttl")

        query = f"select ?x ?z where {{ ?x ns1:label ?z}}"
        df, concept_list = self.format_taxonomy(graph, query)

        return graph, namespace, df, concept_list


class TaxonomyRDFCCS(TaxonomyRDF):
    def __init__(self, path=None):
        super().__init__()
        if path is not None:
            self.path = path
        (
            self.graph,
            self.namespace,
            self.taxonomy,
            self.concept_list,
        ) = self.read_taxonomy()
        self.semantic_search = SemanticSearch(
            data=self.concept_list, tax_name="CCS_RDF"
        ).do_faiss_lookup
        self.lexical_search = LexicalSearch(
            data=self.concept_list, tax_name="CCS_RDF"
        ).lexical_search
        self.rdf_query_children = (
            f"select * where {{ <%(node)s> skos:narrower ?x . ?x skos:prefLabel ?z}}"
        )
        self.rdf_query_parents = (
            f"select * where {{ <%(node)s> skos:broader ?x . ?x skos:prefLabel ?z}}"
        )
        print("Taxonomy instantiated")

    def read_taxonomy(self):
        # fix format
        with open(path_join(self.path, "acm_ccs.xml"), "r") as f:
            content = f.read()

        fixed = content.replace("lang=", "xml:lang=")

        with open(path_join(self.path, "acm_ccs_fixed.xml"), "w") as f:
            f.write(fixed)

        graph = Graph().parse(path_join(self.path, "acm_ccs_fixed.xml"), format="xml")
        namespace = Namespace("")

        query = f"select ?x ?z where {{ ?x skos:prefLabel ?z}}"
        df, concept_list = self.format_taxonomy(graph, query)

        return graph, namespace, df, concept_list
