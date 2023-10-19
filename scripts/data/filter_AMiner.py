import argparse
import json
from datetime import datetime
from os.path import join as join_path
from time import mktime
from concept_rate import ConceptRate
from cso_classifier import CSOClassifier
from keybert import KeyBERT
from tqdm import tqdm

import cld3

MANDATORY_FIELDS = ["abstract", "title", "year", "id"]
OPTIONAL_FIELDS = [
    "keywords", "fos", "url", "pdf", "doi",
    "authors", "venue", "volume", "issue",
    "issn", "isbn", "n_citations", "page_start", "page_end"
]


def extract_docs(in_path: str, out_path: str):
    titles = []
    with open(in_path, "r") as f_in:
        with open(out_path, "w") as f_out:
            for line in tqdm(f_in):
                paper = json.loads(line)

                # Skip paper if the required FIELDS are not available
                if sum([paper.get(key, False) != False for key in MANDATORY_FIELDS]) != len(MANDATORY_FIELDS):
                    continue

                # if the title is repeated, it skips the data
                if paper["title"] in titles:
                    continue
                else:
                    titles.append(paper["title"])

                abstract = paper["abstract"]

                # Skip papers with empty abstract
                if abstract:
                    if len(abstract) == 0 or abstract.__class__ != str or abstract == "N/A":
                        continue
                else:
                    continue

                abstract = abstract.strip()

                references = paper.get("references", [])
                if len(references) == 0:
                    continue

                references = [str(x) for x in references]
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

                year = paper["year"]
                # Skip papers when year is not available
                if year == 0 or year is None:
                    continue
                else:
                    try:
                        """
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

                id = str(paper["id"])

                paper_dict = {
                    "id": id,
                    "title": paper["title"],
                    "abstract": abstract,
                    "year": year,
                    "references": references,
                }

                for field in OPTIONAL_FIELDS:
                    paper_dict[field] = paper[field]

                f_out.write(json.dumps(paper_dict))
                f_out.write("\n")


def add_fields(in_path, out_path):
    concept_rate = ConceptRate(mount_on_gpu=True)
    classifier = CSOClassifier(
        workers=1,
        modules="both",
        enhancement="first",
        explanation=True
    )

    with open(in_path, "r") as f:
        papers = {}
        keywords = []
        abstracts = []
        lengths = []
        for i, line in enumerate(f):
            paper = json.loads(line)
            papers[paper["id"]] = paper
            keywords.append(paper["keywords"])
            lengths.append(len(paper["keywords"]))
            abstracts.append(paper["title"] + ' ' + paper["abstract"])
            if i == 100000:
                break

        CSO_keywords = classifier.batch_run(papers, workers=cpu_count() - 8)
        for i in CSO_keywords.keys():
            papers[i]["CSO_keywords"] = CSO_keywords[i]

        keywords = [keywords[i:i + 100] for i in range(0, len(keywords), 100)]
        abstracts = [abstracts[i:i + 100] for i in range(0, len(abstracts), 100)]
        lengths = [lengths[i:i + 100] for i in range(0, len(lengths), 100)]

        keywords_scored = []
        for kw, abs, lens in zip(keywords, abstracts, lengths):
            keywords_scored.extend(concept_rate.concept_score(concepts=kw,
                                                              documents=abs,
                                                              lengths=lens))

        for i, j in zip(papers.keys(), keywords_scored):
            papers[i]["keywords"] = j

    open(out_path, "w").write("\n".join(json.dumps(papers[i]) for i in papers.keys()))


def main(path: str, concep_processing: bool):
    in_path = join_path(path, "dblpv13.jsonl")
    out_path = join_path(path, "AMiner.jsonl")
    extract_docs(in_path, out_path)

    if concep_processing:
        in_path = out_path
        out_path = join_path(path, "AMiner_processed.jsonl")
        add_fields(in_path, out_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='jsonl dataset filtering')
    parser.add_argument('-p',
                        dest='path',
                        type=str,
                        help='path to the folder which contains the jsonl',
                        default="../../data/external/")
    parser.add_argument('-cp',
                        dest='concep_processing',
                        type=bool,
                        help='flag to process concepts',
                        default=False)

    path = parser.parse_args().path
    concep_processing = parser.parse_args().concep_processing
    main(path, concep_processing)

