import json
from typing import List, Dict


def search_engine_mockup(path_to_file: str) -> List[Dict[str, str]]:
    with open(path_to_file, "r") as json_file:
        json_list = list(json_file)

    results_list = []
    for json_str in json_list:
        result = json.loads(json_str)
        results_list.append(result)
    return results_list
