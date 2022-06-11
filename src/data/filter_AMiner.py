import argparse
import json
from datetime import datetime
from os.path import join as join_path
from time import mktime
from src.dossier_search.concept_search.concept_rate import ConceptRate
from cso_classifier import CSOClassifier
from keybert import KeyBERT

import cld3


MANDATORY_FIELDS = ["abstract", "title", "year", "id"]
OPTIONAL_FIELDS = ["keywords", "fos", "url", "pdf", "doi", "authors", "venue", "volume", "issue",
                   "issn", "isbn", "n_citations", "page_start", "page_end"]


def extract_docs(dataset_path: str):
    concept_rate = ConceptRate()
    classifier = CSOClassifier(workers=1, modules="both", enhancement="first", explanation=True)
    kw_model = KeyBERT()
    papers_dict = {}
    titles = []
    with open(dataset_path, "r") as f_in:
        for line in f_in:
            paper = json.loads(line)

            """Skip paper if the required FIELDS are not available"""
            if sum([paper.get(key, False) != False for key in MANDATORY_FIELDS]) != len(MANDATORY_FIELDS):
                continue
            # todo check all the fields and add new ones
            # if the title is repeated, it skips the data
            if paper["title"] in titles:
                continue
            else:
                titles.append(paper["title"])

            # Abstract
            abstract = paper["abstract"]

            """Skip papers with empty abstract"""
            if abstract:
                if len(abstract) == 0 or abstract.__class__ != str or abstract == "N/A":
                    continue
            else:
                continue

            abstract = abstract.strip()
            # References
            references = paper.get("references", [])
            if len(references) == 0:
                continue

            references = [str(x) for x in references]
            """Remove duplicates from references"""
            references = list(set(references))

            """
            Check abstract language and skip non-english.
            For those papers with lang field not available
            check language trough cld3
            pycld3 is a neural network model for language identification. 
            This package contains the inference code and a trained model.
            """
            if not paper.get("lang", False):
                lang = cld3.get_language(abstract).language
            else:
                lang = paper["lang"]
            if lang.lower() != "en":
                continue

            # year
            year = paper["year"]
            """Skip papers when year is not available"""
            if year == 0 or year is None:
                continue
            else:
                try:
                    """
                    Year will be transformed to a timestamp.
                    This will skip papers with years not provided as 
                    a 4-digits number
                    """
                    int(mktime(datetime.strptime(str(year), "%Y").timetuple()))
                except:
                    continue

            if not paper.get("authors", False):
                paper["authors"] = []

            for field in OPTIONAL_FIELDS:
                if not paper.get(field, False):
                    paper[field] = []

            # id
            id = str(paper["id"])

            # Paper
            papers_dict[id] = {
                "title": paper["title"],
                "abstract": abstract,
                "year": year,
                "references": references,
            }

            for field in OPTIONAL_FIELDS:
                papers_dict[id][field] = paper[field]

            keywords = papers_dict[id]["keywords"]
            if len(keywords) > 0:
                try:
                    papers_dict[id]["keywords_score"] = concept_rate.concept_score(concepts=[keywords],
                                                                                   documents=[abstract],
                                                                                   lengths=[len(keywords)])
                except RuntimeError:
                    pass
            papers_dict[id]["CSO"] = classifier.run(papers_dict[id])

            doc = paper["title"] + ' ' + abstract

            candidates = list(set(papers_dict[id]["keywords"] +
                                  papers_dict[id]["fos"] +
                                  sum([item for _, item in papers_dict[id]["CSO"].items()][:-1], [])))
            keyBert_scores = kw_model.extract_keywords(docs=doc,
                                                       candidates=candidates,
                                                       nr_candidates=len(candidates))
            papers_dict[id]["keyBert_scores"] = keyBert_scores

    return papers_dict


def main(path="./"):
    dataset_path = join_path(path, "dblpv13.jsonl")

    papers_dict = extract_docs(dataset_path)

    docs = [{**{"docno": q_id}, **q_dict} for q_id, q_dict in papers_dict.items()]

    open(join_path(path, "AMiner.jsonl"), "w").write(
        "\n".join(json.dumps(i) for i in docs)
    )


parser = argparse.ArgumentParser(description='jsonl dataset filtering')
parser.add_argument('-p',
                    dest='path',
                    type=str,
                    help='path to the folder which contains the jsonl')

if __name__ == '__main__':
    path = parser.parse_args().path
    path = "../../data/external/"
    main(path)

