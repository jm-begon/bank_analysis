from bank_analysis.base import Account
from bank_analysis.predicate import Predicate, \
    TreePology, KnownOtherParty, TreePologyLeaf, KnownAccount


def treepology_factory(name=None):
    name = "Total" if name is None else name
    return TreePology(
        name,
        TreePology(
            "Grocery",
            *[KnownOtherParty(p) for p in ("3644 COLRUYT ANS", "CORA ROCOURT",
                                           "FERME A L'ARBRE", "CORA SA ROCOURT",
                                           "DELHAIZE LIERS", "MARKET ROCOURT",
                                           "CRF MKT ANS", "HYPER BONCELLES",
                                           "INTERMARCHE AWAN", "ALDI 03 ANS")]
        ),
        TreePology(
            "Ablus",
            *[KnownOtherParty(p) for p in ("TOM&CO AWANS", "CABINET MABIME S",
                                           "ANIMAL CONFORT L")]
        ),
        TreePologyLeaf(KnownOtherParty("FAYEN THIERY", "Fayen")),
        TreePologyLeaf(KnownAccount(Account("BE92750681857723", name="Common"))),
        TreePologyLeaf(KnownAccount(Account("BE64755560262252", name="JM Savings"))),
        TreePologyLeaf(KnownAccount(Account("BE63001334594708", name="JM BNP"))),
        TreePology(
            "State",
            *[KnownAccount(x) for x in
              [Account("BE30679200209111", name="SPF"),
               Account("BE58091215034679", name="taxes")]]
        ),
        TreePologyLeaf(KnownOtherParty("MAKRO ALLEUR STA", "Fuel Makro")),

        TreePologyLeaf(KnownOtherParty("RESTAURANTS UNIV")),
    )
