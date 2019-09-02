import os
from abc import ABCMeta, abstractmethod

from bank_analysis.axa import Payment
from bank_analysis.base import Account, Entity


class Predicate(object, metaclass=ABCMeta):
    def __init__(self, label=None):
        if label is None:
            label = self.__class__.__name__
        self._label = label

    def from_operation_to_name(self, operation):
        other_party = operation.get_other_party()
        if isinstance(other_party, Account):
            return other_party.name
        return other_party

    @property
    def label(self):
        return self._label

    def fall_under_label(self, operation):
        """Whether this `Label` instance is a label for operation `operation`"""
        return False

    def __call__(self, operation):
        return self.fall_under_label(operation)


class EntityPredicate(Predicate):
    def __init__(self, entity):
        super().__init__(entity.name)
        self.entity = entity

    def fall_under_label(self, operation):
        return operation.get_other_party() == self.entity


class Default(Predicate):
    @property
    def label(self):
        return "Unknown"

    def fall_under_label(self, operation):
        return True


class KnownOtherParty(Predicate):
    def __init__(self, other_party, short_name=None):
        super().__init__(other_party if short_name is None else short_name)
        self.other_party = Entity(other_party)

    def fall_under_label(self, operation):
        return self.from_operation_to_name(operation) == self.other_party


class KnownAccount(Predicate):
    def __init__(self, account):
        super().__init__(account.name)
        self.account = account

    def fall_under_label(self, operation):
        return operation.get_other_party == self.account


# ============================================================================ #
class TreePologyNode(object, metaclass=ABCMeta):
    def __init__(self):
        self.money_in = 0
        self.money_out = 0
        self.n_operations = 0

    @property
    def label(self):
        return "n/a"

    def _do_add_op(self, operation):
        if operation.value > 0:
            self.money_in += operation.value
        else:
            self.money_out += operation.value
        self.n_operations += 1

    @abstractmethod
    def add_operation(self, operation):
        pass

    def tree_view(self, depth=0, max_depth=1000, prefix=""):
        if depth >= max_depth:
            return ""
        return "{}{}: {:.2f} - {:.2f} = {:.2f} ({:d} operation(s))" \
               "".format(prefix, self.label, self.money_in, -self.money_out,
                         self.money_in + self.money_out, self.n_operations)


class EntityMatchingNode(TreePologyNode):
    def __init__(self, label="Total"):
        super().__init__()
        self._label = label
        self.entity_node_dict = {}

    def add_operation(self, operation):
        self._do_add_op(operation)
        entity = operation.get_other_party()
        if entity is None or entity.name == "":
            print(operation)
        entity_node = self.entity_node_dict.get(entity)
        if entity_node is None:
            entity_node = TreePologyLeaf(EntityPredicate(entity))
            self.entity_node_dict[entity] = entity_node
        entity_node.add_operation(operation)
        return True

    def __len__(self):
        return len(self.entity_node_dict)

    @property
    def label(self):
        return self._label

    def tree_view(self, depth=0, max_depth=1000, prefix=""):
        s = [super().tree_view(depth, max_depth, prefix)]
        for child in self.entity_node_dict.values():
            tmp = child.tree_view(depth + 1, max_depth, prefix=prefix + " " * 2)
            if len(tmp) > 0:
                s.append(tmp)
        return os.linesep.join(s)


class TreePologyLeaf(TreePologyNode):
    def __init__(self, predicate):
        super().__init__()
        self.predicate = predicate
        self.operations = []

    @property
    def label(self):
        return self.predicate.label

    def add_operation(self, operation):
        if self.predicate(operation):
            self._do_add_op(operation)
            self.operations.append(operation)
            return True
        return False


class TreePology(TreePologyNode):
    def __init__(self, label, *trees):
        super().__init__()
        self.children = [TreePologyLeaf(x) if isinstance(x, Predicate) else x
                         for x in trees]
        self._label = label

    @property
    def label(self):
        return self._label

    def add_operation(self, operation):
        for i, child in enumerate(self.children):
            if child.add_operation(operation):
                self._do_add_op(operation)
                return True
        return False

    def tree_view(self, depth=0, max_depth=1000, prefix=""):
        s = [super().tree_view(depth, max_depth, prefix)]
        for child in self.children:
            tmp = child.tree_view(depth+1, max_depth, prefix=prefix+" "*2)
            if len(tmp) > 0:
                s.append(tmp)
        return os.linesep.join(s)

