from collections import defaultdict


class Leaf(object):
    def __init__(self, predicate):
        self.predicate = predicate
        self.operations = []

    def add_operation(self, operation):
        if self.predicate(operation):
            self.operations.append(operation)
            return True
        return False

    @property
    def label(self):
        return self.predicate.label

    def __iter__(self):
        yield (self.label,), self.operations





class Tree(object):
    def __init__(self, label, children):
        self._label = label
        self.children = children

    def add_operation(self, operation):
        for child in self.children:
            if child.add_operation(operation):
                return True
        return False

    @property
    def label(self):
        return self._label


    def __iter__(self):
        for child in self.children:
            for l, ops in child:
                yield tuple([self.label] + list(l)), ops





class Treepology(object):
    def __init__(self, tree):
        self.tree = tree
        self.remaining_operation = defaultdict(list)

    def add_operation(self, operation):
        if not self.tree.add_operation(operation):
            entity = operation.get_other_party()
            self.remaining_operation[entity].append(operation)

    def __iter__(self):
        for x in self.tree:
            yield x

        for entity, ops in self.remaining_operation.items():
            yield ("Unknown", entity), ops




