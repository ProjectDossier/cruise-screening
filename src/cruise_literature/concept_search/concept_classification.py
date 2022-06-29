from cso_classifier import CSOClassifier


class CSOClassification:
    def __init__(self):
        self.classifier = CSOClassifier(
            workers=1, modules="both", enhancement="first", explanation=True
        )

    def classify_search_result(self, search_result):
        # input format
        """
        papers = { "id1": { "title": '...', "abstract": '...', "keywords": ['...',]},
                   "id2": { "title": '...', "abstract": '...', "keywords": ['...',]}}
        """
        papers = {}
        for article in search_result:
            papers[article.id] = {'title': article.title,
                                  'abstract': article.abstract,
                                  'keywords': article.keywords
                                  }

        concepts = self.classifier.batch_run(papers)

        # output format
        """
        {"id1": {"syntactic": [...], "semantic": [...], "union": [...], "enhanced": [...], "explanation": {...}},
        "id2": {"syntactic": [...], "semantic": [...], "union": [...], "enhanced": [...], "explanation": {...}}}
        """

        for article in search_result:
            article.CSO_keywords = concepts[article.id]['union']

        return search_result
