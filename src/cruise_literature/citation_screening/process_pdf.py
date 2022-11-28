import requests
import grobid_tei_xml


def parse_doc_grobid(url: str) -> grobid_tei_xml.GrobidDocument:
    """
    if not successful then raises requests.HTTPError
    """
    pdf_resp = requests.get(url)
    pdf_resp.raise_for_status()
    grobid_resp = requests.post(
        "https://cloud.science-miner.com/grobid/api/processFulltextDocument",
        files={
            "input": pdf_resp.content,
            "consolidate_Citations": 0,
            "includeRawCitations": 1,
        },
        timeout=60.0,
    )

    grobid_resp.raise_for_status()
    return grobid_tei_xml.parse_document_xml(grobid_resp.text)
