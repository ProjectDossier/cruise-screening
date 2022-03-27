import argparse
import ast
import json
import re
from os.path import join as join_path

parser = argparse.ArgumentParser(description='jsonl formater')
parser.add_argument('-p',
                    dest='path',
                    type=str,
                    help='path to the folder which contains the jsonl')


def get_jsonl_data(path_in, path_out):
    with open(path_in, "r") as f_in:
        with open(path_out, "w") as f_out:

            for line in f_in:
                if line[0] == "{":
                    paper_line = []

                try:
                    paper_line.append(line)
                except:
                    continue

                if line[0] == "}":
                    paper_line = "".join([re.sub("\n|(  )", "", i) for i in paper_line])

                    number_f = []
                    for i in re.findall(r"(\"\w+\" : Number.*?\(\d+\))", paper_line):
                        number_f.append(
                            (i, '{0}{1}'.format(re.search("\"\w+\" : ", i).group(0), re.search("\d+", i).group(0))))
                    for i in number_f:
                        paper_line = paper_line.replace(i[0], i[1])

                    paper_line = re.sub(r" : null| : \"null\"", ' : None', paper_line)
                    paper_line = re.sub('\"_id\"', '\"id\"', paper_line)

                    f_out.write(json.dumps(ast.literal_eval(paper_line)[0]))
                    f_out.write("\n")
                    del paper_line


def main(path):
    print(join_path(path, "dblpv13.json"))
    get_jsonl_data(join_path(path, "dblpv13.json"), join_path(path, "dblpv13.jsonl"))


if __name__ == '__main__':
    path = parser.parse_args().path
    main(path)
