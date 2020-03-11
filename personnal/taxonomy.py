from bank_analysis.axa import Debit
from bank_analysis.base import Entity, Account
from bank_analysis.predicate import KnownOtherParty, KnownAccount, \
    EntityPredicate, Predicate
from bank_analysis.predicate import OrPredicate
from bank_analysis.treepology import Leaf, Tree, Treepology


def grocery():
    return OrPredicate("Grocey",
                       [KnownOtherParty(p) for p in
                        ("3644 COLRUYT ANS", "CORA ROCOURT",
                         "FERME A L'ARBRE", "CORA SA ROCOURT",
                         "DELHAIZE LIERS", "MARKET ROCOURT",
                         "CRF MKT ANS", "HYPER BONCELLES",
                         "INTERMARCHE AWAN", "ALDI 03 ANS")])

def albus():
    return OrPredicate("Ablus",
                       [KnownOtherParty(p) for p in
                        ("TOM&CO AWANS", "CABINET MABIME S",
                         "ANIMAL CONFORT L")])


def bakery():
    return OrPredicate("Bakery",
                       [KnownOtherParty("FAYEN THIERY", "Fayen")])

def common_account():
    return KnownAccount(Account("BE92750681857723", name="Common"))

def jm_account():
    return KnownAccount(Account("BE72750681857016", name="JM"))

def jm_savings():
    return KnownAccount(Account("BE64755560262252", name="JM Savings"))

def jm_bnp():
    return KnownAccount(Account("BE63001334594708", name="JM BNP"))

def jm_accounts():
    return OrPredicate("JM", [jm_account(), jm_savings(), jm_bnp()])

def helene1():
    return KnownAccount(Account("BE04755567350831", name="Helene1"))

def helene2():
    return KnownAccount(Account("BE39750681857319", name="Helene2"))

def helene():
    return OrPredicate("Helene", [helene1(), helene2()])


def state():
    return OrPredicate("State",
                       [KnownAccount(Account("BE30679200209111", name="SPF")),
                        KnownAccount(Account("BE58091215034679", name="taxes"))])


def univ_restaurant():
    return KnownOtherParty("RESTAURANTS UNIV")

def house_fuel():
    return OrPredicate("House fuel",
                       [KnownAccount(Account("BE27240024480073",
                                             name="Piron combustible")),
                        KnownAccount(Account("BE80340053577077",
                                             name="Alain Massuir"))
                        ])


def water():
    return KnownAccount(Account("BE53096360300053", name="CILE"))

def electricity():
    return OrPredicate("Luminus",
                       [KnownAccount(Account("BE76335055459895",
                                             name="Luminus"))])

def voo():
    return KnownAccount(Account("BE05096363600275", name="VOO"))



def charges():
    return OrPredicate("Charges", [house_fuel(), water(), electricity(),
                                   voo()])


def landtax():
    # cadastre
    return KnownAccount(Account("BE55679200260944", name="landtax"))

class Installment(Predicate):
    # Mensualite
    def fall_under_label(self, operation):
        return isinstance(operation, Debit) and \
               operation.get_other_party() == "AXA BANK BELGIUM"

class LifeInsurance(Predicate):
    pass

# 2019 / 9    4/12/19 4/12/19 4/12/19 -248,42 1121,57 Domiciliation europÈenne    BE82001697497168    AG INSURANCE                FAM004790516EUR     "Domiciliation europÈenne rÈcurrente (Core) pour AG INSURANCE Identification du crÈancier: BE81ZZZ0404494849 RÈfÈrence du mandat: 301360413"
# 2019 / 7    3/10/19 3/10/19 3/10/19 -248,42 -48,75  Domiciliation europÈenne    BE82001697497168    AG INSURANCE                FAM004790516EUR     "Domiciliation europÈenne rÈcurrente (Core) pour AG INSURANCE Identification du crÈancier: BE81ZZZ0404494849 RÈfÈrence du mandat: 301360413"
class HouseInsurance(Predicate):
    # TODO make aprt
    pass

class GarbadgeTax(Predicate):
    pass

def alarm():
    # Is there another ?
    return OrPredicate("Alarm",
                       [KnownOtherParty("ALARME INCENDIE", "AIV")])

def heater():
    return KnownAccount(Account("BE39363134178019", name="EDF Luminus NV"))  # Domiciliation

def house():
    return OrPredicate("House", [landtax(), Installment(), # TODO insurances + garbage
                                 alarm(), heater()])

# gardienne
def kid_carer():
    return KnownAccount(Account("BE07750955625166", name="Laurence Feret"))

def kids():
    return OrPredicate("Kids", [kid_carer()])


def make_common_tree():
    return Treepology(Tree("Common spending", [
        Leaf(charges()),
        Leaf(grocery()),
        Leaf(bakery()),
        Leaf(state()),
        # Tree.from_or_predicate(charges()),

        # Tree.from_or_predicate(house()),
        Leaf(house()),
        # Tree.from_or_predicate(kids()),
        Leaf(kids())
        # TODO car ?
    ]))


class DrivingTax(Predicate):
    pass

class CarMaintenance(Predicate):
    pass

def car_fuel():
    return OrPredicate("Car Fuel",
                       [KnownOtherParty("MAKRO ALLEUR STA", "Fuel Makro"),
                        KnownOtherParty("Q8 106361 ANS", "Q8 Ans")])


def make_car():
    pass

def make_insurance():
    pass

def make_big_works():
    pass


def make_misc_jm():
    # Oxfam
    # Fortis
    pass



