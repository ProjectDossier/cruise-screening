from os.path import exists, join
import pandas as pd
import pyterrier as pt
if not pt.started():
    pt.init()


class LexicalSearch:
    def __init__(self, data: list, tax_name: str):
        self.data = data
        self.path = '../../data/processed/taxonomy{}iter_index'.format(tax_name)
        self.indexref = self.get_index()

    def collection_iter(self, collection):
        for idx, text in enumerate(collection):
            yield {'docno': idx,
                   'text': text}

    def get_index(self):
        if exists(join(self.path, 'data.properties')):
            indexref = pt.IndexFactory.of(join(self.path, 'data.properties'))
        else:
            iter_indexer = pt.IterDictIndexer(self.path,
                                              blocks=True,
                                              overwrite=True)

            doc_iter = self.collection_iter(self.data)
            indexref = iter_indexer.index(doc_iter)

        return indexref

    def lexical_search(self, query):
        retr_controls = {"wmodel": "BM25",
                         "string.use_utf": "true",
                         "end": 0,
                         }

        retr = pt.BatchRetrieve(self.indexref,
                                controls=retr_controls)

        res = retr.search(query)

        if len(res) > 0 and res.score.values[0] > 7:
            return self.data[int(res.docno.values[0])]
        else:
            return -100



