from src.Simulation import SimulationManager, Simulation
from src.Output import MeanOutput

import random
import time


class CounterSimulation(Simulation):
    def run(self):
        amount = self.input
        while True:
            if amount == 0:
                return 0
            elif amount == 100:
                return 1
            else:
                amount += random.choice([-1, 1])


if __name__ == "__main__":
    output = MeanOutput()
    similation_manager = SimulationManager(30, CounterSimulation, output)
    similation_manager.start()
    time.sleep(0.01)
    print(f"{len(output.all_simulations[30])}: {output.aggregate()}")
    time.sleep(0.01)
    print(f"{len(output.all_simulations[30])}: {output.aggregate()}")
    time.sleep(1)
    print(f"{len(output.all_simulations[30])}: {output.aggregate()}")
    similation_manager.stop()
