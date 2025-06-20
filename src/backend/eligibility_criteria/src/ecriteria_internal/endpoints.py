from typing import Callable

from flask import Flask, Response, request

from ecriteria.output import present_model_output
from ecriteria.validation import validate_xml
from ecriteria_internal.model import ModelConfig


def create_generate_pico(app: Flask, model: ModelConfig) -> Callable:
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
            max_tokens = app.config["MAX_TOKENS"]
            temperature = app.config["TEMPERATURE"]

            messages = [
                {"role": "system", "content": instruction},
                {"role": "user", "content": input_text},
            ]
            prompt = model.tokenizer.apply_chat_template(messages, tokenize=False)
            inputs = model.tokenizer(prompt, return_tensors="pt").to(model.device)
            output = model.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                generation_config=model.gen_config,
                temperature=temperature,
            )
            answer = model.tokenizer.decode(output[0], skip_special_tokens=True)[len(prompt):].lstrip()

            return Response(response=f"<response><answer>{present_model_output(answer)}</answer></response>",
                            mimetype='application/xml')
        except Exception as e:
            app.logger.exception("Unexpected failure in generate_combined")
            return Response(response=f"<error>Unexpected failure: {str(e)}</error>",
                            status=500,
                            mimetype='application/xml')

    return generate_pico