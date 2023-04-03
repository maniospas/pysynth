from pysynth.data.collections import Collection, UniqueCollection
from typing import Iterable
from itertools import chain


class Variable:
    """A source code variable to be added to inputs and/or outputs."""
    def __init__(self, name, specifications: Iterable[str], default: str = None):
        self.name = name
        self.specifications = Collection(specifications)
        self.default = default

    def __sub__(self, other):
        return Variable(self.name, self.specifications-other.specifications, self.default)

    def __str__(self):
        if self.default is not None:
            return self.name+" = "+self.default
        return self.name

    def __hash__(self):
        return self.name.__hash__()

    def __add__(self, other):
        return Variable(self.name, self.specifications+other.specifications, self.default)

    def __eq__(self, other):
        if self.specifications-other.specifications:
            return False
        if other.specifications-self.specifications:
            return False
        if self.expressions-other.expressions:
            return False
        if other.expressions-self.expressions:
            return False
        return True

    @property
    def expressions(self):
        return Collection()

    @property
    def inputs(self):
        return UniqueCollection()

    @property
    def outputs(self):
        return UniqueCollection()


class Expression:
    def __init__(self, source):
        self.source = source
        self.dependencies = []

    def __hash__(self):
        return self.__str__().__hash__()

    def align(self, map):
        raise NotImplementedError()


class SourceCodeLine(Expression):
    """A single line of source code tied to a specific source and dependencies."""
    def __init__(self, text: Iterable[str], source=None, dependencies: Iterable[Expression] = None):
        super().__init__(source)
        self.text = list(text)
        self.dependencies = Collection() if dependencies is None else Collection(dependencies)
        self.tostr = "".join(self.text)

    def __hash__(self):
        return self.tostr.__hash__()

    def __str__(self):
        return self.tostr

    def align(self, map):
        for k, v in map.items():
            self.text = [v.name if pred == k.name else pred for pred in self.text]
        self.tostr = "".join(self.text)
        #for k, v in map.items():
        #    self.text = self.text.replace(k.name, v.name)

    def copy(self):
        return SourceCodeLine(self.text, self.source, self.dependencies)


class Model:
    """A model comprising specifications, expressions, and input and output variables."""

    def __init__(self,
                 specifications: Iterable[str],
                 expressions: Iterable[Expression],
                 inputs: Iterable[Variable],
                 outputs: Iterable[Variable]):
        self.specifications = Collection(specifications)
        self.inputs = UniqueCollection(inputs)
        self.outputs = UniqueCollection(outputs)
        self.expressions = Collection(expressions)

    def copy(self):
        return Model(self.specifications, [expr.copy() for expr in self.expressions], self.inputs, self.outputs)

    def augment(self):
        prev_specs = self.specifications
        for var in self.vars:
            self.specifications = self.specifications + var.specifications
        #for var in self.vars:
        #    var.specifications += prev_specs
        return self

    @property
    def vars(self):
        return self.inputs + self.outputs

    def align(self, map):
        for expression in self.expressions:
            expression.align(map)
        for k, v in map.items():
            if k in self.inputs:
                self.inputs.remove(k)
                self.inputs.add(v)
            if k in self.outputs:
                self.outputs.remove(k)
                self.outputs.add(v)

    def __sub__(self, other):
        return Model(self.specifications-other.specifications,
                     self.expressions-other.expressions,
                     self.inputs,
                     self.outputs)

    def __add__(self, other):
        return Model(self.specifications+other.specifications,
                     self.expressions+other.expressions,
                     self.inputs+other.inputs,
                     self.outputs+other.outputs)

    def __eq__(self, other):
        if self.specifications-other.specifications:
            return False
        if other.specifications-self.specifications:
            return False
        if self.expressions-other.expressions:
            return False
        if other.expressions-self.expressions:
            return False
        return True

    def order(self):
        outs = dict()
        ins = dict()
        for expr in self.expressions:
            splt = str(expr).split("=")
            if len(splt) < 2:
                ins[expr] = set([var.name for var in self.inputs if var.name in expr.text])
                continue
            outs[expr] = set([var.name for var in self.outputs if var.name in splt[0]])
            ins[expr] = set([var.name for var in self.inputs if var.name in splt[1]])
        changes = 1
        for _ in range(10):
            if changes == 0:
                break
            changes = 0
            for i in range(len(self.expressions)):
                for j in range(i+1, len(self.expressions)):
                    if self.expressions[j] in outs and self.expressions[i] in ins and outs[self.expressions[j]].intersection(ins[self.expressions[i]]):
                        changes += 1
                        self.expressions[i], self.expressions[j] = self.expressions[j], self.expressions[i]
        return self

    @property
    def dependencies(self):
        return set(chain.from_iterable(expr.dependencies for expr in self.expressions))

    @property
    def source(self):
        return set(chain.from_iterable(expr.source for expr in self.expressions if expr.source))

    def __str__(self):
        self.order()
        dependencies = '\n'.join(set(str(expr) for expr in self.dependencies))
        code = '\n'.join(str(expr) for expr in self.expressions)
        ret = f"Specifications: {' '.join(self.specifications)}\n" \
              f"Inputs: {self.inputs}\n" \
              f"Outputs: {self.outputs}\n" \
              f"{dependencies}\n"\
              f"{code}"
        return ret

    def __hash__(self):
        return id(self)
