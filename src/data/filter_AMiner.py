from os.path import join as join_path
import argparse
from datetime import datetime
from time import mktime
import json
import cld3

FIELDS = ["abstract", "title", "year", "id", "keywords"]


def extract_docs(dataset_path):
    papers_dict = {}

    with open(dataset_path, "r") as f_in:
        for line in f_in:
            paper = json.loads(line)

            """Skip paper if the required FIELDS are not available"""
            if sum([paper.get(key, False) != False for key in FIELDS]) != len(FIELDS):
                continue

            # keywords
            keywords = paper["keywords"]
            if len(keywords) == 0:
                continue

            # Abstract
            abstract = paper["abstract"]

            """Skip papers with empty abstract"""
            if abstract:
                if len(abstract) == 0 or abstract.__class__ != str or abstract == "N/A":
                    continue
            else:
                continue

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
                    t = int(mktime(datetime.strptime(str(year), "%Y").timetuple()))
                    timestamp = t if t > 0 else 0
                except:
                    continue

            # id
            id = str(paper["id"])

            if not paper.get("authors", False):
                paper["authors"] = []

            if not paper.get("venue", False):
                paper["venue"] = []

            # Paper
            papers_dict[id] = {
                "title": paper["title"],
                "document": abstract,
                "timestamp": timestamp,
                "keywords": keywords,
                "authors": paper["authors"],
                "venue": paper["venue"],
                "references": references
            }

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
    main(path)

