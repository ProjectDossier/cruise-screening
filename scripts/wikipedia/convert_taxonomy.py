import json
import xml.etree.cElementTree as ET


def convert_wikipedia_taxonomy_to_xml(
    infile: str = "../../data/external/wikipedia_taxonomy.json",
):
    with open(infile) as fp:
        content = json.load(fp)

    root = ET.Element(
        "rdf:RDF",
        attrib={
            "xmlns:rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "xmlns:skos": "http://www.w3.org/2004/02/skos/core#",
        },
    )

    for item in content:
        doc = ET.SubElement(root, "skos:Concept", attrib={"rdf:about": item["url"]})
        title = item["title"]
        if title.startswith("Category:"):
            title = title[9:]  # Remove 'Category:' from the title

        ET.SubElement(doc, "skos:prefLabel", attrib={"lang": "en"}).text = title

        for child_url, child_name in item["children"].items():
            ET.SubElement(
                doc,
                "skos:narrower",
                attrib={"rdf:resource": f"https://en.wikipedia.org{child_url}"},
            )

        for parent_url, parent_name in item["parents"].items():
            ET.SubElement(
                doc,
                "skos:broader",
                attrib={"rdf:resource": f"https://en.wikipedia.org{parent_url}"},
            )

    tree = ET.ElementTree(root)
    tree.write(
        "../../data/external/wikipedia_taxonomy.xml",
        xml_declaration=True,
        encoding="UTF-8",
    )


if __name__ == "__main__":
    convert_wikipedia_taxonomy_to_xml()
