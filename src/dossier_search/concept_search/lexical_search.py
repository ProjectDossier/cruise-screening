from os.path import exists, join
import pandas as pd
import pyterrier as pt
if not pt.started():
    pt.init()


class LexicalSearch:
    def __init__(self, data: pd.DataFrame, tax_name: str):
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
        retr_controls = {"wmodel": "TF_IDF",
                         "string.use_utf": "true",
                         "end": 0,
                         }

        retr = pt.BatchRetrieve(self.indexref,
                                controls=retr_controls)

        idx = int(retr.search(query).docno.values[0])
        return self.data[idx]



