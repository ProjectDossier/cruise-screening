import json
import xml.etree.cElementTree as ET


def convert_wikipedia_taxonomy_to_xml():
    with open("/scripts/result.json") as fp:
        content = json.load(fp)

    root = ET.Element(
        "rdf:RDF",
        attrib={
            "xmlns:rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "xmlns:skos": "http://www.w3.org/2004/02/skos/core#",
        },
    )

    for item in content:
        doc = ET.SubElement(root, f"skos:Concept", attrib={"rdf:about": item["url"]})
        ET.SubElement(doc, f"skos:prefLabel", attrib={"lang": "en"}).text = item[
            "title"
        ][:-12]

        for child_url, child_name in item["children"].items():
            ET.SubElement(
                doc,
                f"skos:narrower",
                attrib={"rdf:resource": f"https://en.wikipedia.org{child_url}"},
            )

        for parent_url, parent_name in item["parents"].items():
            ET.SubElement(
                doc,
                f"skos:broader",
                attrib={"rdf:resource": f"https://en.wikipedia.org{parent_url}"},
            )

    tree = ET.ElementTree(root)
    tree.write("wikipedia_taxonomy.xml", xml_declaration=True, encoding="UTF-8")


if __name__ == "__main__":
    convert_wikipedia_taxonomy_to_xml()
