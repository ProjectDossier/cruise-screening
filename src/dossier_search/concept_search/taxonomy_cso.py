import pandas as pd
import xmltodict
from concept import Concept
from fuzzywuzzy import fuzz
import csv


class Taxonomy_CSO:
    def __init__(self, path):
        self.path = path
        self.taxonomy_rows = []
        self.concept_id_pairs = {}
        self.get_csv(path)
        self.assign_IDs()

        print("Taxonomy instantiated")

    def get_csv(self, path):
        with open(path, "r") as f:
            csvreader = csv.reader(f)
            for row in csvreader:
                self.taxonomy_rows.append(row)
    def assign_IDs(self):
        ID_counter = 1
        for row in self.taxonomy_rows:
            concept = row[0].split('/')[-1]
            if concept in self.concept_id_pairs.keys():
                continue
            self.concept_id_pairs[concept] = ID_counter
            ID_counter += 1






if __name__ == "__main__":
    cso_tax = Taxonomy_CSO ('D:/PythonProjects/cruise-literature/data/external/CSO.3.2.csv')
    print("End")
