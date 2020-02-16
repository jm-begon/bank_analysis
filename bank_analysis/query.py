"""
A query operates on an historic an prodives a query report.

Examples
--------
In/Out ratio
What is the money spent into
Who is getting money in, and how much
How much is sent to account x
etc.
"""
import os
from abc import ABCMeta, abstractmethod
from collections import defaultdict

from bank_analysis.predicate import Default, TreePologyLeaf, EntityMatcher
from .base import Account


class Query(object, metaclass=ABCMeta):
    @abstractmethod
    def query(self, historic):
        pass

    def __call__(self, historic):
        return self.query(historic)


class InOutQuery(Query):
    def query(self, historic):
        accounts = set()
        oldest, latest = historic.period_covered()
        total = defaultdict(float)
        number_of_ops = defaultdict(int)
        for operation in historic:
            accounts.add(operation.account.account_to_str(type=False))
            key = "in" if operation.value > 0 else "out"
            total[key] += operation.value
            number_of_ops[key] += 1

        return """
============
In/Out query
============
Period: {} - {}
Accounts: {}

in:    {:.2f} ({} operations)
out:  {:.2f} ({} operations)
-----------------------
total: {:.2f}
""".format(oldest, latest, ", ".join(accounts), total["in"],
           number_of_ops["in"], total["out"],
           number_of_ops["out"], total["in"]+total["out"])


class SpendingAnalysis(Query):
    def __init__(self, *labels):
        self.labels = list(labels) + [Default()]

    def _detail(self, total, n_ops):
        s = ""
        for key, value in total.items():
            s += "{}: {:.2f} ({} operations){}" \
                 "".format(key, value, n_ops[key], os.linesep)
        return s.strip()

    def query(self, historic):
        accounts = set()
        oldest, latest = historic.period_covered()
        # TODO manage automatically this
        total = defaultdict(float)
        n_ops = defaultdict(int)

        for operation in historic:
            if operation.value > 0:
                continue
            accounts.add(operation.account.account_to_str(type=False))

            for label in self.labels:
                if label(operation):
                    total[label.label] += operation.value
                    n_ops[label.label] += 1
                    break
        return """
=================
Spending analysis
=================
Period: {} - {}
Accounts: {}

{}
-----------------------------
total: {:.2f}
""".format(oldest, latest, ", ".join(accounts),
           self._detail(total, n_ops),
           sum(total.values()))


class HierarchicalAnalysis(Query):
    def __init__(self, treepology, max_depth=1000, give_unknown=False):
        self.tree = treepology
        self.max_depth = max_depth
        self.give_unknown = give_unknown

    def query(self, historic):
        accounts = set()
        oldest, latest = historic.period_covered()

        unknown = EntityMatcher()
        for operation in historic:
            if not self.tree.add_operation(operation):
                unknown.add_operation(operation)
            accounts.add(operation.account.account_to_str(type=False))
        unknown_str = ""
        if self.give_unknown:
            unknown_str = ", ".join([repr(o) for o in unknown])
            unknown_str += os.linesep

        tree_str = self.tree.tree_view(max_depth=self.max_depth)
        return """
=======
Typlogy
=======
Period: {} - {}
Accounts: {}

Known entities
-----------------------------
{}

{:d} unknown entitie(s)
-----------------------------
{}
""".format(oldest, latest, ", ".join(accounts),
           self.tree.tree_view(max_depth=self.max_depth),
           len(unknown),
           unknown.tree_view(max_depth=self.max_depth))
