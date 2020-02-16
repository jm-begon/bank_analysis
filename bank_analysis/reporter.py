from bank_analysis.predicate import Predicate


class Reporter(object):
    def __init__(self):
        self.n_operations = 0
        self.plus = 0
        self.minus = 0

    def register_operation(self, operation):
        self.n_operations += 1
        if operation.is_gain():
            self.plus += operation.value
        else:
            self.minus += operation.value

    def __str__(self):
        return "{:.2f} - {:.2f} = {:.2f} ({:d} operation(s))" \
               "".format(self.plus, self.minus, self.plus + self.minus,
                         self.n_operations)


class Observer(Predicate):
    def __init__(self, predicate, reporter):
        super().__init__(predicate.label)
        self.predicate = predicate
        self.reporter = reporter

    def fall_under_label(self, operation):
        if self.predicate(operation):
            self.reporter.register_operation(operation)

    def __str__(self):
        return "{}: {}".format(self.label, str(self.reporter))


class TreeObserver(Predicate):
    @classmethod
    def build_observer(cls, treepology, reporter_factory, max_depth):
        pass

    def __init__(self, treepology, reporter_factory, max_depth=5):
        super().__init__(treepology.label)
        self.tree = self.__class__.build_observer(treepology, reporter_factory,
                                                  max_depth)


    def fall_under_label(self, operation):
        return self.tree(operation)




