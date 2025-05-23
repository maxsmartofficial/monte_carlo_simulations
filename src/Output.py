from .ResultBatch import ResultBatch
from typing import Any
from collections import defaultdict


class Output:
    def __init__(self):
        self.all_simulations = defaultdict(list)
        self.latest_input = None
        self.current_input = None

    def _get_input(self):
        if self.current_input is None:
            return self.latest_input
        else:
            return self.current_input

    def get_simulations(self):
        return self.all_simulations[self._get_input()]

    def aggregate(self) -> list[Any]:
        return self.get_simulations()

    def update(self, value: ResultBatch):
        values = value.batch
        input = value.input
        self.all_simulations[input] += values
        self.latest_input = input
        self.handle_update(values)

    def handle_update(self, values: list) -> None:
        pass

    def set_input(self, input):
        self.current_input = input


class MeanOutput(Output):
    def aggregate(self) -> float:
        return sum(self.get_simulations()) / len(self.get_simulations())
