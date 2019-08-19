from abc import ABCMeta
from datetime import datetime

import copy
from dateutil.parser import parse as auto_parse_date


class Operation(object, metaclass=ABCMeta):
    @classmethod
    def parse_date(cls, date):
        if isinstance(date, datetime):
            return date
        return auto_parse_date(date)

    def __init__(self, account, operation_date, effective_date, value,
                 description):
        self.account = account
        self.op_date = self.__class__.parse_date(operation_date)
        self.effective_date = self.__class__.parse_date(effective_date)
        self.value = float(value)
        self.description = description

    def __repr__(self):
        return "{cls}(account={account}, operation_date={operation_date}, " \
               "effective_date={effective_date}, value={value}," \
               "description={description})" \
               "".format(cls=self.__class__.__name__,
                         account=repr(self.account),
                         operation_date=repr(self.op_date.strftime("%d/%m/%Y")),
                         effective_date=repr(self.effective_date.strftime("%d/%m/%Y")),
                         value=repr(self.value),
                         description=repr(self.description))

    def is_loss(self):
        return self.value < 0

    def is_gain(self):
        return self.value > 0

    def get_other_party(self):
        pass


class Bank(object):
    def __init__(self, name, bic):
        self.name = name
        self.bic = bic

    def __repr__(self):
        return "{cls}(name={name}, bic={bic})" \
               "".format(cls=self.__class__.__name__,
                         name=repr(self.name),
                         bic=repr(self.bic))

    def __eq__(self, other):
        return isinstance(other, Bank) and  other.name == self.name and \
               self.bic == other.bic


class Account(object):
    def __init__(self, iban, bank=None, name="n/a", type="n/a"):
        self.iban = iban
        self.bank = bank
        self.name = name
        self.type = type

    def __repr__(self):
        return "{cls}(iban={iban}, bank={bank}, name={name}, type={type})" \
               "".format(cls=self.__class__.__name__,
                         iban=repr(self.iban),
                         bank=repr(self.bank),
                         name=repr(self.name),
                         type=repr(self.type))

    def account_to_str(self, bank=True, name=True, type=True):
        s = self.iban
        if bank and self.bank is not None:
            s += " @ {}".format(self.bank)
        if name and self.name != "n/a":
            s += " ({})".format(self.name)
        if type and self.type != "n/a":
            s += " {}".format(self.type)
        return s

    def __str__(self):
        return self.account_to_str()

    def __eq__(self, other):
        return isinstance(other, Account) and \
               self.iban.replace(" ", "") == other.iban.replace(" ", "")

    def __hash__(self):
        return hash(repr(self))


class Historic(object):
    def __init__(self, operations=None):
        if operations is None:
            operations = []
        self.operations = [x for x in operations]

    def __getitem__(self, item):
        if isinstance(item, slice):
            new_historic = copy.copy(self)
            new_historic.operations = new_historic.operations[item]
            return new_historic
        return self.operations[item]

    def merge(self, other_historic):
        # TODO filter out redoundancy
        new_historic = copy.copy(self)
        new_historic.operations = copy.copy(self.operations)
        new_historic.operations.extend(other_historic.operations)
        return new_historic

    def period_covered(self):
        oldest = None
        latest = None
        for op in self.operations:
            if oldest is None or op.op_date < oldest:
                oldest = op.op_date
            if latest is None or latest < op.op_date:
                latest = op.op_date
        return oldest, latest

    def filter(self, predicate):
        clone = copy.copy(self)
        remaining_ops = [op for op in clone.operations if predicate(op)]
        clone.operations = remaining_ops
        return clone

    def clip(self, oldest=None, latest=None):
        def predicate(operation):
            return (oldest is None or oldest <= operation.op_date) and \
                   (latest is None or operation.op_date <= latest)
        return self.filter(predicate)




