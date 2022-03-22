import pandas as pd
import xmltodict


path = "/Users/oscarespitia/Downloads/cruise-literature/src/data/acm_ccs.xml"
with open(path, "r") as f:
    text = f.read()
    examples = xmltodict.parse(text)['rdf:RDF']['skos:Concept']

id = '@rdf:about'
name = 'skos:prefLabel'
childs = 'skos:narrower'
child = '@rdf:resource'
example_list = []
for example in examples:
    try:
        if len(example[childs]) == 1:
            example[childs] = [example[childs]]
        for e_child in [i[child].split('.')[-1] for i in example[childs]]:
            example_list.append([example[id].split('.')[-1],
                                 example[name]['#text'],
                                 e_child])
    except:
        example_list.append([example[id].split('.')[-1], example[name]['#text'], None])


table = pd.DataFrame(example_list, columns=["id", "text", "child"])
table = table.drop_duplicates()
id = table[table.text == "Evolutionary robotics"].id.values[0]
past_id = []


def recursive_search(query):
    id = table[table.child == query].id.values
    if len(id) == 0:
        return [query]
    elif len(id) == 1:
        return [query] + recursive_search(id[0])
    else:
        return [query] + [recursive_search(i) for i in id]


list_ = recursive_search(id)
print(list_)







