from collections import defaultdict


class Leaf(object):
    def __init__(self, predicate):
        self.predicate = predicate
        self.operations = []

    def reset(self):
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

    def prefix_walk(self):
        return iter(self)

    def __len__(self):
        return len(self.operations)





class Tree(object):
    @classmethod
    def from_or_predicate(cls, or_predicate, depth=1):
        if depth != 1:
            raise NotImplementedError("Soon. Maybe.")
        return cls(or_predicate.label, [Leaf(x) for x in or_predicate])

    def __init__(self, label, children):
        self._label = label
        self.children = children

    def reset(self):
        for child in self.children:
            child.reset()

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

    def prefix_walk(self):
        all_ops = []
        child_stuff = []
        for label, ops in self:
            child_stuff.append((label, ops))
            all_ops.extend(ops)

        yield (self.label,), all_ops
        for x in child_stuff:
            yield x

    def __len__(self):
        s = 0
        for child in self.children:
            s += len(child)
        return s



class Grouper(object):
    def __init__(self, label="Unknown"):
        self._label = label
        self.groups = defaultdict(list)

    @property
    def label(self):
        return self._label

    def reset(self):
        self.groups = defaultdict(list)

    def add_operation(self, operation):
        entity = operation.get_other_party()
        self.groups[entity].append(operation)
        return True

    def __iter__(self):
        for entity, ops in self.groups.items():
            yield (self.label, entity), ops


    def prefix_walk(self):
        all_ops = []
        all_labels = []
        for entity, ops in self.groups.items():
            all_labels.append((self.label, entity))
            all_ops.append(ops)
        yield (self.label,), [item for sublist in all_ops for item in sublist]

        for label, op in zip(all_labels, all_ops):
            yield label, op

    def items(self):
        return self.groups.items()


    def __len__(self):
        s = 0
        for ops in self.groups.values():
            s += len(ops)
        return s


class Treepology(object):
    def __init__(self, tree):
        self._tree = tree
        self.remaining_operation = Grouper("Unknown")

    def reset(self):
        self.tree.reset()
        self.remaining_operation.reset()

    @property
    def tree(self):
        return self._tree

    @property
    def unknowns(self):
        return self.remaining_operation


    def add_operation(self, operation):
        if not self._tree.add_operation(operation):
            self.remaining_operation.add_operation(operation)

    def iter_knowns(self):
        for x in self._tree:
            yield x

    def iter_unknowns(self):
        for x in self.remaining_operation:
            yield x

    def __iter__(self):
        for x in self._tree:
            yield x
        for x in self.remaining_operation:
            yield x


    def prefix_walk(self):
        return iter(self._tree.prefix_walk())


    def __len__(self):
        return len(self._tree) + len(self.remaining_operation)