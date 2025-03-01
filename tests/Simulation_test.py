import unittest
from unittest.mock import Mock
from src.Simulation import SimulationManager, Simulation
from queue import Queue

class MockSimulation(Simulation):
    def run(self):
        return self.input


class SimulationManagerTest(unittest.TestCase):
    def test_simulation_manager_writes_to_output(self):
        mock_output = Mock()

        simulation_manager = SimulationManager(input=10, simulation_type=MockSimulation, output=mock_output)
        simulation_manager.start(processes=1, runs=1)
        simulation_manager.stop()
        mock_output.update.assert_called_once_with(10)

    

class SimulationTest(unittest.TestCase):
    def test_simulation_writes_to_queue(self):
        result_queue = Queue()
        simulation = MockSimulation(input = 10, result_queue=result_queue)
        simulation.start()
        self.assertFalse(result_queue.empty())
        result = result_queue.get(block=False)
        self.assertEqual(result, 10)



