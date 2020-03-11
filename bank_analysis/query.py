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

from datetime import datetime, timedelta

from bank_analysis.formating.util import format_tree_view, \
    format_tree_view_as_str
from bank_analysis.predicate import Default, OrPredicate, MoneyOut
from bank_analysis.treepology import Tree, Treepology
from .base import Account

def list_months(start_date, end_date):
    mi = start_date.month
    yi = start_date.year
    final = datetime(end_date.year, end_date.month, 1)
    while True:
        start = datetime(yi, mi, 1)
        if start >= final:
            break
        mi += 1
        if mi > 12:
            mi = 1
            yi += 1
        end = datetime(yi, mi, 1) - timedelta(seconds=1)
        yield start, end


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


class ProvisionQuery(Query):
    def do_query(self, historic):
        oldest, latest = historic.period_covered()
        accounts = set()
        total = defaultdict(float)
        number_of_ops = defaultdict(int)
        for operation in historic:
            if operation.value < 0:
                continue

            accounts.add(operation.account.account_to_str(type=False))
            key = operation.get_other_party().name
            total[key] += operation.value
            number_of_ops[key] += 1

        summary = []
        for key in total.keys():
            summary.append("{:20} {:.2f} ({} operations)"
                           "".format(key, total[key], number_of_ops[key]))

        return """
Period: {} - {}
Accounts: {}

{}
-----------------------
total: {:.2f}
        """.format(oldest, latest, ", ".join(accounts), "\n".join(summary),
                   sum(total.values()))

    def query(self, historic):
        oldest, latest = historic.period_covered()
        reports = []
        for start, end in list_months(oldest, latest):
            s = self.do_query(historic.clip(start, end))
            reports.append(s)

        reports.append(self.do_query(historic))


        return """
================
Provision query
================
{}
        """.format("\n\n".join(reports))





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
        if isinstance(treepology, Tree):
            self.tree = Treepology(treepology)
        self.max_depth = max_depth
        self.give_unknown = give_unknown

    def query(self, historic):
        accounts = set()
        oldest, latest = historic.period_covered()

        for operation in historic:
            self.tree.add_operation(operation)
            accounts.add(operation.account.account_to_str(type=False))
        unknown = self.tree.remaining_operation.keys()
        unknown_str = ""
        if self.give_unknown:
            unknown_str = ", ".join([repr(o) for o in unknown])
            unknown_str += os.linesep

        def gen_op_info(treepology):
            for label, ops in treepology.prefix_walk():
                v = "{:.2f} ({} operations)".format(sum(op.value for op in ops),
                                                    len(ops))
                yield label, v


        l = list(format_tree_view_as_str(gen_op_info(self.tree)))
        tree_str = "\n".join(l)

        # tree_str = self.tree.tree_view(max_depth=self.max_depth)
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
           tree_str,
           self.tree.unknown_size(),
           unknown_str)


class MonthlySpendingQuery(Query):
    def __init__(self, treepology, max_depth=1000, give_unknown=False):
        self.treepology = treepology
        self.max_depth = max_depth
        self.give_unknown = give_unknown

    def format_level(self, label, ops):
        return "{:.2f} ({} operations)".format(sum(op.value for op in ops),
                                               len(ops))

    def gen_op_info(self, generator):
        for label, ops in generator:
            v = "{:.2f} ({} operations)".format(sum(op.value for op in ops),
                                                len(ops))
            yield label, self.format_level(label, ops)

    def do_query(self, historic):
        oldest, latest = historic.period_covered()

        for operation in historic:
            self.treepology.add_operation(operation)

        unknowns = self.treepology.unknowns
        l = list(format_tree_view_as_str(self.gen_op_info(unknowns.prefix_walk())))
        if self.give_unknown:
            unknown_str = "\n".join(l)
        else:
            unknown_str = l[0]


        l = list(format_tree_view_as_str(self.gen_op_info(self.treepology.tree.prefix_walk())))
        tree_str = "\n".join(l)

        return """
Period: {} - {}

Known entities
-----------------------------
{}

Unknown entities
-----------------------------
{}
""".format(oldest, latest, tree_str, unknown_str)

    def query(self, historic):
        historic = historic.filter(MoneyOut())

        # Suppose only one account
        oldest, latest = historic.period_covered()
        reports = []
        for start, end in list_months(oldest, latest):
            self.treepology.reset()
            s = self.do_query(historic.clip(start, end))
            reports.append(s)

        self.treepology.reset()
        reports.append(self.do_query(historic))

        return """
====================================
Hierarchical Spending Analysis query
====================================
{}
        """.format("\n\n".join(reports))