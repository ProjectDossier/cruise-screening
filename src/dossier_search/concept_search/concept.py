from dataclasses import dataclass


@dataclass
class Concept:
    id: str
    text : str
    _parents = []
    _children = []

    @property
    def parents(self):
        return self._parents

    @parents.setter
    def parents(self, parents):
        self._parents = parents

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, children):
        self._children = children
