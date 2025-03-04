import unittest
from unittest.mock import Mock, call
from src.Simulation import SimulationManager, Simulation
from threading import Event


class MockSimulation(Simulation):
    def run(self):
        return self.input


class MockCounterOutput:
    def __init__(self, limit, limit_flag):
        self.counter = 0
        self.limit = limit
        self.limit_flag = limit_flag

    def update(self, value):
        self.counter += 1
        if self.counter == self.limit:
            self.limit_flag.set()


class SimulationManagerTest(unittest.TestCase):
    def test_simulation_manager_writes_to_output(self):
        mock_output = Mock()

        simulation_manager = SimulationManager(
            input=10, simulation_type=MockSimulation, output=mock_output
        )
        simulation_manager.start(runs=1)
        mock_output.update.assert_called_once_with(10)

    def test_many_simulations_run(self):
        mock_output = Mock()

        simulation_manager = SimulationManager(
            input=10, simulation_type=MockSimulation, output=mock_output
        )
        simulation_manager.start(runs=5)
        mock_output.update.assert_has_calls([call(10)] * 5)

    def test_run_indefinitely(self):
        done = Event()
        mock_output = MockCounterOutput(2, done)

        simulation_manager = SimulationManager(
            input=10, simulation_type=MockSimulation, output=mock_output
        )
        simulation_manager.start()
        done.wait()
        simulation_manager.stop()
        self.assertGreater(mock_output.counter, 0)


class SimulationTest(unittest.TestCase):
    def test_simulation_writes_to_queue(self):
        simulation = MockSimulation(input=10)
        result = simulation.start()
        self.assertEqual(result, 10)


if __name__ == "__main__":
    unittest.main()
