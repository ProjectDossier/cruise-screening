from typing import Callable

from flask import Flask, Response, request
from google.genai import Client
from google.genai.types import GenerateContentConfig

from ecriteria.output import present_model_output
from ecriteria.validation import validate_xml


def create_generate_pico(app: Flask, client: Client) -> Callable:
    def generate_pico():
        input_xml = request.data
        try:
            validate_xml(input_xml)
        except ValueError as error:
            app.logger.exception(str(error))
            return Response(response=f"<error>Input does not pass the validation</error>",
                            status=500,
                            mimetype='application/xml')

        try:
            instruction = app.config["INSTRUCTION"]
            input_text = input_xml.decode("utf-8")
            model = app.config["GEN_MODEL"]
            max_tokens = app.config["MAX_TOKENS"]
            temperature = app.config["TEMPERATURE"]

            answer = client.models.generate_content(
                model=model,
                contents=input_text,
                config=GenerateContentConfig(
                    system_instruction=instruction,
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                ),
            ).text

            return Response(f"<response><answer>{present_model_output(answer)}</answer></response>",
                            mimetype='application/xml')
        except Exception as e:
            app.logger.exception("Unexpected failure in generate_combined")
            return Response(response=f"<error>Unexpected failure: {str(e)}</error>",
                            status=500,
                            mimetype='application/xml')

    return generate_pico