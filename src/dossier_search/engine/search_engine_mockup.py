import json

path_to_file = '/home/fps/Downloads/AMiner_sample_l10.jsonl'


def search_engine_mockup():
    with open(path_to_file, 'r') as json_file:
        json_list = list(json_file)

    results_list = []
    for json_str in json_list:
        result = json.loads(json_str)
        results_list.append(result)
        print(f"result: {result}")
    return results_list