from .ResultBatch import ResultBatch
from typing import Any


class Output:
    def __init__(self):
        self.all_simulations = []

    def aggregate(self) -> list[Any]:
        return self.all_simulations

    def update(self, value: Any | ResultBatch):
        if isinstance(value, ResultBatch):
            self.all_simulations += value.batch
        else:
            self.all_simulations.append(value)


class MeanOutput(Output):
    def aggregate(self) -> float:
        return sum(self.all_simulations) / len(self.all_simulations)
