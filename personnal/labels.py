from bank_analysis.base import Account
from bank_analysis.predicate import Predicate, \
    KnownOtherParty, KnownAccount, OrPredicate
from bank_analysis.treepology import Leaf, Tree, Treepology


def treepology_factory(name=None):
    name = "Total" if name is None else name
    return Treepology(
        Tree(name, [
            Leaf(
                OrPredicate(
                    "Grocey",
                    [KnownOtherParty(p) for p in
                     ("3644 COLRUYT ANS", "CORA ROCOURT",
                      "FERME A L'ARBRE", "CORA SA ROCOURT",
                      "DELHAIZE LIERS", "MARKET ROCOURT",
                      "CRF MKT ANS", "HYPER BONCELLES",
                      "INTERMARCHE AWAN", "ALDI 03 ANS")]
                )
            ),
            Leaf(
                OrPredicate(
                    "Ablus",
                    [KnownOtherParty(p) for p in
                     ("TOM&CO AWANS", "CABINET MABIME S",
                      "ANIMAL CONFORT L")]
                )
            ),
            Leaf(KnownOtherParty("FAYEN THIERY", "Fayen")),
            Leaf(KnownAccount(Account("BE92750681857723", name="Common"))),
            Leaf(KnownAccount(Account("BE64755560262252", name="JM Savings"))),
            Leaf(KnownAccount(Account("BE63001334594708", name="JM BNP"))),
            Leaf(
                OrPredicate(
                    "State",
                    [KnownAccount(x) for x in
                     [Account("BE30679200209111", name="SPF"),
                      Account("BE58091215034679", name="taxes")]]
                )
            ),
            Leaf(KnownOtherParty("MAKRO ALLEUR STA", "Fuel Makro")),
            Leaf(KnownOtherParty("RESTAURANTS UNIV"))
        ]),
    )
