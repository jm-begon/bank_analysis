"""
A query operates on an historic an prodives a query report.

Examples
--------
In/Out ratio
What is the money spent into
Who is getting money in, and how much
etc.
"""
from collections import defaultdict


class Query(object):
    def __call__(self, historic):
        pass


class InOutQuery(object):
    def __call__(self, historic):
        accounts = set()
        oldest, latest = historic.period_covered()
        total = defaultdict(float)
        number_of_ops = defaultdict(int)
        for operation in historic:
            accounts.add(operation.account.account_to_str(type=False))
            key = "in" if operation.value > 0 else "out"
            total[key] += operation.value
            number_of_ops[key] += 1

        return """In/Out query
------------
Period: {} - {}
Accounts: {}

in:    {:.2f} ({} operations)
out:  {:.2f} ({} operations)
-----------------------
total: {:.2f}
""".format(oldest, latest, ", ".join(accounts), total["in"],
           number_of_ops["in"], total["out"],
           number_of_ops["out"], total["in"]+total["out"])
