from dataclasses import dataclass


@dataclass
class Concept:
    def __init__(self, id: str, text: str):
        self.id = id
        self.text = text
        self.parents = []
        self.children = []

    def set_parents(self, parents):
        self.parents = parents

    def set_children(self, children):
        self.children = children
