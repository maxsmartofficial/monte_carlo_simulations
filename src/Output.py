from .ResultBatch import ResultBatch


class Output:
    def __init__(self):
        self.all_simulations = []

    def aggregate(self):
        return self.all_simulations

    def update(self, value):
        if isinstance(value, ResultBatch):
            self.all_simulations += value.batch
        else:
            self.all_simulations.append(value)


class MeanOutput(Output):
    def aggregate(self):
        return sum(self.all_simulations) / len(self.all_simulations)
