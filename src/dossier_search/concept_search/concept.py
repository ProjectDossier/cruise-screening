from dataclasses import dataclass


@dataclass
class Concept:
    id: str
    text: str
    children_ids: str = ""
    parent_ids: str = ""
    _parents = []
    _children = []

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.id == other.id and self.text == other.text
        return False

    def __hash__(self):
        return hash(self.id) ^ hash(self.text)

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
