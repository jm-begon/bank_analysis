from bank_analysis.base import Entity
from bank_analysis.predicate import Predicate, Treepology, EntityPredicate




class FuelOil(Predicate):
    def __init__(self):
        super().__init__("FuelOil")
        self.entities = {Entity("Piron combustible")}  # TODO
        # Alain Massuir - BE80 340 0535770 77


    def fall_under_label(self, operation):
        return operation.get_other_party() in self.entities



def make_charges():
    return Treepology("Charges", (
        EntityPredicate(Entity("CILE")),
        EntityPredicate(Entity("Luminus")),
        EntityPredicate(Entity("VOO")),
        EntityPredicate(Entity("EDF LUMINUS NV")),  # Domiciliation chaudiere
        FuelOil(),
    ))

class Installment(Predicate):
    # Mensualite
    pass

class LifeInsurance(Predicate):
    pass

class LandTax(Predicate):
    # Cadastre
    pass

class HouseInsurance(Predicate):
    # TODO make aprt
    pass

class Alarm(Predicate):
    pass

class Heater(Predicate):
    pass

def make_house():
    return Treepology("House", (Installment, LifeInsurance, LandTax,
                                HouseInsurance, Alarm, Heater))

class GarbadgeTax(Predicate):
    pass

class Grocery(Predicate):
    pass

def make_misc_common():
    pass

class DrivingTax(Predicate):
    pass

class Maintenance(Predicate):
    pass


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

# gardienne