from pysynth.synthesis.base import Synthesizer
from typing import Iterable


class Greedy(Synthesizer):
    def __call__(self, query):
        while True:
            next_query = self.step(query)
            if next_query == query:
                break
            query = next_query
        return query


class Multispecs:
    def __init__(self, synthesizer: Synthesizer):
        self.synthesizer = synthesizer

    def __call__(self, specifications: str):
        specifications = specifications.replace(" and ", "\n").replace(",", "\n")
        assert "\n" in specifications  # force multiclause specifications to avoid common usage bugs
        specifications = [spec.strip() for spec in specifications.split("\n") if spec.strip()]

        from pysynth import specs, Model
        specifications = list(specifications)
        result = Model(specs(specifications[0]), [], [], [])
        result = self.synthesizer(result)
        remainder = result.specifications
        for spec in specifications[1:]:
            result.specifications = specs(spec)
            result = self.synthesizer(result)
            remainder += result.specifications
        result.specifications = remainder
        return result



