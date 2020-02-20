import os
import warnings
from abc import ABCMeta
from collections import namedtuple

import re

from .base import Operation, Bank, Account, Historic, Entity


class AxaBank(Bank):
    def __init__(self):
        super().__init__("Axa", "AXABBE22")

    def __repr__(self):
        return "{}()".format(self.__class__.__name__)


class AxaOp(Operation):
    # Always try to be more specific
    def __init__(self, account, operation_date, effective_date, value,
                 description, amount_remaining, message=""):
        super().__init__(account, operation_date, effective_date, value,
                         description)
        self.amount_remaining = amount_remaining
        self.message = message


class NotAccountOp(AxaOp, metaclass=ABCMeta):
    """The other party is not an account"""
    def __init__(self, account, operation_date, effective_date, value,
                 description, amount_remaining, other_party_name,
                 other_party_place, message=""):
        super().__init__(account, operation_date, effective_date, value,
                         description, amount_remaining, message)
        self.other_party_name = Entity(other_party_name)
        self.other_party_place = other_party_place

    def get_other_party(self):
        return self.other_party_name


class Payment(NotAccountOp):
    pass


class Withdrawal(NotAccountOp):
    pass



class AccountOp(AxaOp, metaclass=ABCMeta):
    def __init__(self, account, operation_date, effective_date, value,
                 description, amount_remaining, other_party_account,
                 other_party_name, message=""):
        super().__init__(account, operation_date, effective_date, value,
                         description, amount_remaining, message)

        self.other_party = Account(iban=other_party_account,
                                   name=other_party_name)

    def get_other_party(self):
        return self.other_party


class Transfer(AccountOp):
    pass


class PossiblyWithinOperation(AccountOp):
    def get_other_party(self):
        other = super().get_other_party()
        if isinstance(other, Account) and other.name == "":
            return self.account.bank
        return other


class Debit(PossiblyWithinOperation):
    """Like fiscal domiciliation"""
    pass


class PermanentOrder(AccountOp):
    pass


class VisaDebit(Debit):
    pass


class Fee(PossiblyWithinOperation):
    def get_other_party(self):
        return self.account.bank


class AxaParser(object):
    OpStr = namedtuple('OpStr', ['id', 'operation_date', 'effective_date',
                                 'writing_date', 'value', 'amount_remaining',
                                 'type', 'other_account', 'other_name',
                                 'machine_name', 'place', 'card_number',
                                 'msg1', 'msg2', 'details'])

    def _parse_general_header(self, hdl, account_name):
        bank = AxaBank()
        type = hdl.readline().strip()
        account_str = hdl.readline()
        bic_str = hdl.readline()
        for _ in range(5):
            # Skip useless lines
            hdl.readline()

        iban = account_str[5:].replace(" ", "").strip()
        bic = bic_str[4:].strip()
        if bank.bic != bic:
            print(len(bank.bic))
            print(len(bic))
            raise ValueError("BIC of the bank is not correct. "
                             "Expecting {}, found {}".format(bank.bic, bic))
        return Account(iban, bank, account_name, type=type)

    def _parse_operation(self, line, line_number, account):
        op_str = self.__class__.OpStr(*line.split(";"))
        # Selecting on type

        other_is_account = False
        other_is_not_account = False
        if op_str.type == "Achat - Bancontact" or \
           op_str.type == "Achat - Maestro" or \
           op_str.type == "Vente glob. - Bancontact":
            factory = Payment
            other_is_not_account = True
        elif op_str.type.startswith("Retrait"):
            factory = Withdrawal
            other_is_not_account = True
        elif op_str.type.startswith("Virement") or \
            op_str.type == "Epargne Automatique":
            factory = Transfer
            other_is_account = True
        elif op_str.type == "Ordre permanent":
            factory = PermanentOrder
            other_is_account = True
        elif op_str.type.startswith("Domiciliation") or \
             op_str.type == "Encaissement interne":
            if "visa" in op_str.type.lower():
                factory = VisaDebit
            else:
                factory = Debit
            other_is_account = True
        elif op_str.type.startswith("Contribution") or \
            op_str.type ==  "Tarification: ATM":
            factory = Fee
            other_is_account = True
        elif op_str.type == "Capitalisation":
            factory = Fee  # Weird
            other_is_account = True
        else:
            warnings.warn("Unknown operation type '{}' (line {})."
                          "".format(op_str.type, line_number))
            factory = AxaOp

        def partial(**kwargs):
            return factory(account=account,
                           operation_date=op_str.operation_date,
                           effective_date=op_str.effective_date,
                           value=float(op_str.value.replace(",", ".")),
                           description=op_str.details,
                           amount_remaining=op_str.amount_remaining,
                           message=os.linesep.join([op_str.msg1, op_str.msg2]),
                           **kwargs)

        if other_is_account:
            return partial(other_party_account=op_str.other_account,
                           other_party_name=op_str.other_name)
        elif other_is_not_account:
            return partial(other_party_name=op_str.machine_name,
                           other_party_place=op_str.place)
        else:
            return partial()

    def parse_csv(self, fpath, account_name="n/a", encoding="latin"):
        ops = []
        line_start = re.compile(r"^\d\d\d\d(\s)?/(\s)?\d+")
        with open(fpath, "r", encoding=encoding) as hdl:
            account = self._parse_general_header(hdl, account_name)
            header_line = hdl.readline().strip()  # skip csv header
            curr_line = ""
            for i, line in enumerate(hdl):
                if line_start.match(line):
                    if len(curr_line) > 0:
                        ops.append(self._parse_operation(curr_line.strip(),
                                                         i + 8,
                                                         account))
                    curr_line = line
                else:
                    curr_line += line
                last_line = curr_line
            if len(curr_line) > 0:
                ops.append(self._parse_operation(curr_line.strip(),
                                                 "last line",
                                                 account))

        return Historic(ops)
