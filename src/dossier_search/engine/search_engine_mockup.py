#import json
from typing import List, Dict



res1 = {"id": "53e99784b7602d9701f3e15d", "title": "Timing yield estimation", "url": "https://www.", "snippet": "str", "abstract": "str", "authors": "[{'id': '53f43b64dabfaefedbaf97e4', 'name': 'Ilias Michalarias', 'org': 'Corresponding author. Tel.: +49 30 838 75132; fax: +49 30 838 75196.', 'orgs': ['Corresponding author. Tel.: +49 30 838 75132; fax: +49 30 838 75196.', 'Freie Universit Berlin, Garystr. 21, 14195 Berlin, Germany'], 'email': 'ilmich@wiwiss.fu-berlin.de', 'sid': '3528692'}, {'id': '53f43354dabfaedd74d80e7b', 'name': 'Arkadiy Omelchenko', 'org': 'Freie Universit Berlin, Garystr. 21, 14195 Berlin, Germany', 'orgs': ['Freie Universit Berlin, Garystr. 21, 14195 Berlin, Germany'], 'sid': '3134003', 'orgid': '5f71b29a1c455f439fe3d008'}, {'id': '53f443b6dabfaeecd69a25b7', 'name': 'Hans-Joachim Lenz', 'org': 'Freie Universit Berlin, Garystr. 21, 14195 Berlin, Germany', 'orgs': ['Freie Universit Berlin, Garystr. 21, 14195 Berlin, Germany'], 'sid': '28138', 'orgid': '5f71b29a1c455f439fe3d008'}]", "publication_date": "str", "venue": "{'sid': 'data-and-knowledge-engineering', 'issn': '0169-023X', 't': 'J', 'raw': 'Data & Knowledge Engineering', 'publisher': 'North-Holland'}"}
res2 = {"id": "53e99784b7602d9701f3f411", "title": "Using XML to Integrate ", "url": "https://www.", "snippet": "str", "abstract": "str", "authors": "[{'id': '53f43b03dabfaedce555bf2a', 'name': 'Min Pan'}, {'id': '53f45ee9dabfaee43ecda842', 'name': 'Chris C. N. Chu'}, {'id': '53f42e8cdabfaee1c0a4274e', 'name': 'Hai Zhou'}]", "publication_date": "str", "venue": "{'id': '53a72e2020f7420be8c80142', 'name_d': 'International Symposium on Circuits and Systems', 'type': 0, 'raw': 'ISCAS (3)'}"}
res3 = {"id": "53e99784b7602d9701f3f5fe", "title": "Research on resource allocation", "url": "https://www.", "snippet": "str", "abstract": "str", "authors": "[{'id': '548a2e3ddabfae9b40134fbc', 'name': 'Harry M. Sneed'}]", "publication_date": "str", "venue": "{'id': '53a72e9920f7420be8c93fac', 'name_d': 'Computer Software and Applications Conference', 'type': 0, 'raw': 'COMPSAC'}"}
res4 = {"id": "53e99784b7602d9701f3f95d", "title": "FCLOS", "url": "https://www.", "snippet": "str", "abstract": "str", "authors": "[{'id': '53f43640dabfaedf4357edfc', 'name': 'Pradip Thomas', 'org': 'Tel.: +61 7 336 52915.', 'orgs': ['Tel.: +61 7 336 52915.', 'School of Journalism, University of Queensland, Brisbane, Qld. 4072, Australia'], 'email': 'Pradip.thomas@uq.edu.au', 'sid': '51711430'}]", "publication_date": "str", "venue": "{'sid': 'telematics-and-informatics', 'issn': '0736-5853', 't': 'J', 'raw': 'Telematics and Informatics', 'publisher': 'Pergamon'}"}


#def search_engine_mockup(path_to_file: str) -> List[Dict[str,str]]:
#    with open(path_to_file, 'r') as json_file:
#        json_list = list(json_file)
#
#    results_list = []
#    for json_str in json_list:
#        result = json.loads(json_str)
#        results_list.append(result)
#    return results_list

def search_eng_mockup() -> List[Dict[str,str]]:

    results_list = []
    results_list.append(res1)
    results_list.append(res2)
    results_list.append(res3)
    results_list.append(res4)
    return results_list
