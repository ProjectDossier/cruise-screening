from Bio import Entrez, Medline
from cruise_literature.settings import ENTREZ_EMAIL
from document_search.utils import SearchResultWithStatus
from utils.article import Article, generate_uuid
from utils.article import Author

Entrez.email = ENTREZ_EMAIL


def search_pubmed(query: str, top_k: int) -> SearchResultWithStatus:
    """
    Search PubMed for a given query and return a list of articles.
    :param query: a search query
    :param top_k: number of results to return
    :return:
    """
    try:
        handle = Entrez.esearch(db="pubmed", term=query, retmax=top_k)
        records = Entrez.read(handle)
        id_list = records["IdList"]
        handle.close()

        handle = Entrez.efetch(
            db="pubmed", id=id_list, rettype="medline", retmode="text"
        )
        candidate_list = []
        for record in Medline.parse(handle):
            authors = []
            for author in record.get("FAU", []):
                display_name = author
                first_name = author.split(",")[0]

                authors.append(Author(display_name=display_name, first_name=first_name))

            doi = next(
                (
                    _potential_id[:-4].strip()
                    for _potential_id in record.get("LID", [""]).split("]")
                    if _potential_id.strip().startswith("10.")
                ),
                None,
            )

            uuid = generate_uuid()
            retrieved_art = Article(
                id=uuid,
                pmid=record["PMID"],
                semantic_scholar_id=None,
                core_id=None,
                doi=doi,
                title=record["TI"],
                url=f"https://pubmed.ncbi.nlm.nih.gov/{record['PMID']}/",
                pdf=None,
                snippet=record["AB"][:300],
                abstract=record["AB"],
                authors="; ".join([a.display_name for a in authors]),
                publication_date=record["MHDA"][:4],  # get full date
                venue=record["JT"],
                keywords_snippet=record.get("OT", []),
                keywords_rest=None,
                CSO_keywords=None,
                n_citations=None,
                n_references=None,
            )
            candidate_list.append(retrieved_art)

        _status = "OK"
        _status_code = 200
    except IOError:
        _status = "ERROR"
        _status_code = 500
        candidate_list = []

    return {
        "results": candidate_list,
        "status": _status,
        "status_code": _status_code,
        "search_engine": "PubMed",
        "search_query": query,
    }
