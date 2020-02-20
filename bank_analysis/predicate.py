from abc import ABCMeta, abstractmethod

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


class FalsePredicate(Predicate):
    def fall_under_label(self, operation):
        return False


class OrPredicate(Predicate):
    def __init__(self, label=None, predicates=None):
        super().__init__(label)
        if predicates is None:
            predicates = []
        self.predicates = predicates

    def fall_under_label(self, operation):
        for predicate in self.predicates:
            if predicate(operation):
                return True
        return False


class MoneyIn(Predicate):
    def fall_under_label(self, operation):
        return operation.value > 0


class MoneyOut(Predicate):
    def fall_under_label(self, operation):
        return operation.value < 0


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


# # ============================================================================ #
# class Treepology(OrPredicate):
#     @classmethod
#     def predicate_to_node(cls, predicate):
#         if not isinstance(predicate, Treepology):
#             t = Treepology(predicate.label)
#             t.predicates.append(predicate)
#             return t
#         return predicate
#
#     def __init__(self, label=None, predicates=None):
#         if predicates is None:
#             predicates = []
#         super().__init__(label, [self.__class__.predicate_to_node(x)
#                                  for x in predicates])
#
#     @property
#     def children(self):
#         return self.predicates
#
#     def append(self, predicate):
#         self.predicates.append(self.__class__.predicate_to_node(predicate))
#
#     def tree_to_dict(self, d=None):
#         d = {} if d is None else d
#         d[self.label] = self
#         for child in self.children:
#             child.tree_to_dict(d)
#         return d
#
#
# class EntityMatcher(Predicate):
#     def __init__(self, label=None):
#         super().__init__(label)
#         self.known_entities = {}
#
#     def fall_under_label(self, operation):
#         entity = operation.get_other_party()
#         p = self.known_entities.get(entity)
#         if p is None:
#             p = EntityPredicate(entity)
#             self.known_entities[entity] = p
#         return p(entity)  # Which should always be True
#
