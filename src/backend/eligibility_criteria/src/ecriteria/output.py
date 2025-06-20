def present_model_output(output: str) -> str:
    return output.strip().removeprefix('```xml').removesuffix('```').strip()