from cso_classifier import CSOClassifier


class CSOClassification:
    def __init__(self):
        self.classifier = CSOClassifier(workers=1, modules="both", enhancement="first", explanation=True)

    def classify_search_result(self, search_result):
        # input format
        """
        papers = { "id1": { "title": '...', "abstract": '...', "keywords": ['...',]},
                   "id2": { "title": '...', "abstract": '...', "keywords": ['...',]}}
        """
        papers = {}
        for article in search_result:
            papers[article.id] = {'title': article.title,
                                  'abstract': article.snippet + ' ' + article.abstract,
                                  'keywords': article.keywords_snippet + article.keywords_rest
                                  }

        concepts = self.classifier.batch_run(papers)

        # output format
        """
        {"id1": {"syntactic": [...], "semantic": [...], "union": [...], "enhanced": [...], "explanation": {...}},
        "id2": {"syntactic": [...], "semantic": [...], "union": [...], "enhanced": [...], "explanation": {...}}}
        """

        for article in search_result:
            article.CSO = concepts[article.id]

        return search_result
