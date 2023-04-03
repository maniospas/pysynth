class Complexity:
    def __init__(self, simplicity=0.1):
        assert simplicity > 0
        self.simplicity = simplicity

    def __call__(self, model):
        return len(model.specifications) - self.simplicity*len(model.expressions)


class Equivalence:
    def __init__(self, database, complexity):
        self.database = database
        self.complexity = complexity

    def __call__(self, model1, model2):
        if model1 == model1-model2:
            return False
        from pysynth.data import Variable
        if not isinstance(model1, Variable):
            return True
        #print("--------")
        match = self.complexity(model1-(model1-model2))
        #print(model1, model2)
        #print(model1.specifications, model2.specifications)
        for k, v in self.database:
            if k is model1 or k is model2:
                continue
            if model1-k != model1:
                if self.complexity(model1-(model1-k)) > match:
                    #print("prevented by", k.specifications, (model1-(model1-k)).specifications)
                    return False
            if model2-k != model1:
                if self.complexity(model2-(model2-k)) > match:
                    #print("prevented by", k.specifications, (model2-(model2-k)).specifications)
                    return False
        return True


class Synthesizer:
    def __init__(self, database, equivalence=Equivalence, complexity=Complexity()):
        self.database = database
        self.equivalence = equivalence(database, complexity)
        self.var_equivalence = equivalence(database.vardatabase(), complexity)
        self.complexity = complexity

    def __call__(self, query):
        return self.step(query)

    def step(self, query, selector=max):
        candidates = list()
        for specs, impl in self.database:
            diff = query - specs
            if self.equivalence(query-diff, specs):
                candidates.append((diff, specs, impl))
        if not candidates:
            return query
        diff, specs, impl = selector(candidates, key=lambda entry: self.complexity(query-entry[0])-self.complexity(entry[0])-self.complexity(entry[2]))
        align_map = dict()
        for var1 in query.vars:
            for var2 in impl.vars:
                if self.var_equivalence(var1, var2+diff):
                    align_map[var2] = var1  # the order does not matter
        query = diff + impl.copy()
        query.align(align_map)
        return query
