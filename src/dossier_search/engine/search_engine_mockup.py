path_to_file = '/home/fps/Downloads/AMiner_sample_l10.jsonl'

with open(path_to_file, 'r', encoding='utf-8') as reader:
    for line in reader:
        print(line)
        break

import json

data = json.load(path_to_file)

import json

with open(path_to_file, 'r') as json_file:
    json_list = list(json_file)

for json_str in json_list:
    result = json.loads(json_str)
    print(f"result: {result}")
    print(isinstance(result, dict))
    break

result['docno']
result['title']
