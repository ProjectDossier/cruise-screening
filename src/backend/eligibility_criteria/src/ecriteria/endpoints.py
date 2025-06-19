from typing import Callable

from flask import Response, Flask, request

def create_request_entity_too_large(app: Flask) -> Callable:
    def request_entity_too_large(error):
        app.logger.error(f"Payload too large: {error}")
        return Response("<error>Request too large. Limit is 8192 bytes.</error>", status=413,
                        mimetype='application/xml')

    return request_entity_too_large

def create_validate(app: Flask) -> Callable:
    def validate():
        max_length = app.config.get('MAX_CONTENT_LENGTH', 8192)
        if max_length and len(request.data) > max_length:
            return Response("<error>Request too large. Limit is 8192 bytes.</error>", status=413,
                            mimetype='application/xml')

        try:
            tree = ET.fromstring(request.data)
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

            xml_input_str = ET.tostring(xml_input_elem, encoding='unicode', method='xml')
            inner_xml = xml_input_str.replace('<xml_input>', '').replace('</xml_input>', '').strip()
            response_xml = f"<validated>{inner_xml}</validated>"
            return Response(response_xml, mimetype='application/xml')

        except Exception as e:
            app.logger.exception("Validation error")
            error_xml = f"<error>Invalid XML input: {str(e)}</error>"
            return Response(error_xml, status=400, mimetype='application/xml')

    return validate
