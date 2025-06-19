import xml.etree.ElementTree as ET

def transform_xml(input_xml: str) -> str:
    xml_input_elem = ET.fromstring(input_xml).find("xml_input")

    xml_input_str = ET.tostring(xml_input_elem, encoding='unicode', method='xml')
    inner_xml = xml_input_str.replace('<xml_input>', '').replace('</xml_input>', '').strip()
    response_xml = f"<validated>{inner_xml}</validated>"

    return response_xml