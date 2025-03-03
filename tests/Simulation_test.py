import unittest
from unittest.mock import Mock, call
from src.Simulation import SimulationManager, Simulation


class MockSimulation(Simulation):
    def run(self):
        return self.input


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


class SimulationTest(unittest.TestCase):
    def test_simulation_writes_to_queue(self):
        simulation = MockSimulation(input=10)
        result = simulation.start()
        self.assertEqual(result, 10)
