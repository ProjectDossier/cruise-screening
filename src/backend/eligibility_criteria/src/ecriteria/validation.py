import xml.etree.ElementTree as ET


def validate_xml(input_xml: bytes) -> None:
    tree = ET.fromstring(input_xml)
    if tree.tag != "request":
        raise ValueError("Root tag must be <request>.")

    xml_input_elem = tree.find("xml_input")
    if xml_input_elem is None:
        raise ValueError("Missing <xml_input> section.")

    abstract_elem = xml_input_elem.find("article_abstract")
    if abstract_elem is None:
        raise ValueError("Missing <article_abstract> inside <xml_input>.")

    valid_tags = {
        "article_title", "background", "objectives",
        "selection_criteria", "main_results", "authors_conclusions",
        "search_methods", "data_collection_and_analysis"
    }

    for child in abstract_elem:
        if child.tag not in valid_tags:
            raise ValueError(f"Invalid tag found in <article_abstract>: <{child.tag}>")
        if child.tail and child.tail.strip():
            raise ValueError(f"Unexpected text after tag <{child.tag}>")

    if abstract_elem.tail and abstract_elem.tail.strip():
        raise ValueError("Unexpected text found after <article_abstract>")