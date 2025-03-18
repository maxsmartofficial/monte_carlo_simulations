import unittest
from unittest.mock import Mock, call, patch
from src.Simulation import SimulationManager, Simulation, SimulationProcess, ResultBatch
from threading import Event
from multiprocessing import Value


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


class MockPerfCounter:
    def __init__(self):
        self.start = 0

    def perf_counter(self):
        self.start += 1
        return self.start


class SimulationManagerTest(unittest.TestCase):
    def test_simulation_manager_writes_to_output(self):
        mock_output = Mock()

        simulation_manager = SimulationManager(
            input=10, simulation_type=MockSimulation, output=mock_output, batching=False
        )
        simulation_manager.start(runs=1)
        mock_output.update.assert_called_once_with(10)

    def test_many_simulations_run(self):
        mock_output = Mock()

        simulation_manager = SimulationManager(
            input=10, simulation_type=MockSimulation, output=mock_output, batching=False
        )
        simulation_manager.start(runs=5)
        self.assertEqual(mock_output.update.call_args_list, [call(10)] * 5)

    def test_run_indefinitely(self):
        done = Event()
        mock_output = MockCounterOutput(2, done)

        simulation_manager = SimulationManager(
            input=10, simulation_type=MockSimulation, output=mock_output, batching=False
        )
        simulation_manager.start()
        done.wait()
        simulation_manager.stop()
        self.assertGreater(mock_output.counter, 0)

    def test_batched_result(self):
        mock_output = Mock()
        simulation_manager = SimulationManager(
            input=10, simulation_type=MockSimulation, output=mock_output
        )
        simulation_manager.start(runs=200)
        first_output = mock_output.update.call_args_list[0]
        self.assertIsInstance(first_output[0][0], ResultBatch)


class SimulationTest(unittest.TestCase):
    def test_simulation_writes_to_queue(self):
        simulation = MockSimulation(input=10)
        result = simulation.start()
        self.assertEqual(result, 10)


class SimulationProcessTest(unittest.TestCase):
    def test_average_simulation_time(self):
        mock_perf_counter = MockPerfCounter()
        result_queue = Mock()
        mock_simulating = Mock()
        mock_simulating.is_set.return_value = True
        mock_value = Value("i", 2)
        with patch("src.Simulation.time.perf_counter", mock_perf_counter.perf_counter):
            simulation_process = SimulationProcess(
                input=10,
                result_queue=result_queue,
                simulation_type=MockSimulation,
                simulating=mock_simulating,
                total_runs=mock_value,
                batching=False,
            )
            simulation_process.run()

            avg_simulation_time = simulation_process.get_average_simulation_time()
            self.assertEqual(avg_simulation_time, 1)

    def test_average_aggregation_time(self):
        mock_perf_counter = MockPerfCounter()
        result_queue = Mock()
        mock_simulating = Mock()
        mock_simulating.is_set.return_value = True
        mock_value = Value("i", 2)
        with patch("src.Simulation.time.perf_counter", mock_perf_counter.perf_counter):
            simulation_process = SimulationProcess(
                input=10,
                result_queue=result_queue,
                simulation_type=MockSimulation,
                simulating=mock_simulating,
                total_runs=mock_value,
                batching=False,
            )
            simulation_process.run()

            avg_aggregation_time = simulation_process.get_average_aggregation_time()
            self.assertEqual(avg_aggregation_time, 1)


if __name__ == "__main__":
    unittest.main()
