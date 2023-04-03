from pysynth.data.domain import Model
from typing import Iterable


class Database:
    def __init__(self, models: Iterable[Model] = None):
        self.map = dict()
        if models is not None:
            for model in models:
                self.add(model)

    def add(self, model: Model):
        specs = Model(model.specifications, [], [], [])
        impl = Model([], model.expressions, model.inputs, model.outputs)
        self.map[specs] = impl

    def vardatabase(self):
        database = Database()
        database.map = {var: var for k, v in self for model in [k, v] for var in model.vars}
        return database

    def __iter__(self):
        return self.map.items().__iter__()
