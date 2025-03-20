import multiprocessing
import threading
import os
from .ResultBatch import ResultBatch
import time
from .Output import Output
from typing import Any, Optional


class ResultDispatcher(threading.Thread):
    def __init__(
        self,
        result_queue: multiprocessing.Queue,
        output: Output,
        is_dispatching: threading.Event,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.result_queue = result_queue
        self.output = output
        self.is_dispatching = is_dispatching

    def run(self):
        while self.is_dispatching.is_set():
            if self.result_queue.empty():
                continue
            result = self.result_queue.get()
            self.output.update(result)


class SimulationProcess(multiprocessing.Process):
    def __init__(
        self,
        input: int,
        result_queue: multiprocessing.Queue,
        simulation_type: type,
        simulating: multiprocessing.Event,
        total_runs: Optional[multiprocessing.Value] = None,
        batching: bool = False,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.input = input
        self.result_queue = result_queue
        self.simulation_type = simulation_type
        self.simulating = simulating
        self.total_runs = total_runs
        self.batching = batching

        self.batch = []

        self.simulation_time_sum = 0
        self.total_simulations = 0
        self.aggregation_time_sum = 0
        self.total_aggregations = 0

        self.batch_size_cache = None

    def process_result(self, result: Any | ResultBatch) -> None:
        if self.batching:
            self.batch.append(result)
            if len(self.batch) == self.get_batch_size():
                batch = ResultBatch(self.batch)
                start = time.perf_counter()
                self.result_queue.put(batch)
                end = time.perf_counter()
                self.aggregation_time_sum += end - start
                self.total_aggregations += 1
                self.batch = []
                self.recalculate_batch_size()
        else:
            start = time.perf_counter()
            self.result_queue.put(result)
            end = time.perf_counter()
            self.aggregation_time_sum += end - start
            self.total_aggregations += 1

    def more_simulations_required(self) -> bool:
        if self.total_runs is None:
            return True
        with self.total_runs.get_lock():
            if self.total_runs.value <= 0:
                return False
            else:
                self.total_runs.value -= 1
                return True

    def run(self) -> None:
        while self.simulating.is_set():
            if not self.more_simulations_required():
                break
            simulation = self.simulation_type(self.input)
            start = time.perf_counter()
            result = simulation.start()
            end = time.perf_counter()
            self.simulation_time_sum += end - start
            self.total_simulations += 1

            self.process_result(result)

    def get_average_simulation_time(self) -> float:
        if self.total_simulations == 0:
            return 0
        else:
            return self.simulation_time_sum / self.total_simulations

    def get_average_aggregation_time(self) -> float:
        if self.total_aggregations == 0:
            return 0
        else:
            return self.aggregation_time_sum / self.total_aggregations

    def recalculate_batch_size(self) -> None:
        avg_simulation_time = self.get_average_simulation_time()
        avg_aggregation_time = self.get_average_aggregation_time()
        max_batch_size = (avg_aggregation_time / avg_simulation_time) * (
            self.total_simulations
        ) ** 0.5
        batch_size = max(1, min(max_batch_size, self.total_simulations))
        self.batch_size_cache = batch_size

    def get_batch_size(self) -> int:
        if self.batch_size_cache is None:
            self.recalculate_batch_size()

        return self.batch_size_cache


class SimulationManager:
    def __init__(
        self, input: int, simulation_type: type, output: Output, batching: bool = True
    ):
        self.input = input
        self.simulation_type = simulation_type
        self.output = output
        self.batching = batching

    def _run_simulation_process(self) -> Any:
        simulation = Simulation(self.input)
        result = simulation.start()

        return result

    def reset_state(self) -> None:
        self.result_queue = multiprocessing.Queue()
        self.simulating_event_flag = multiprocessing.Event()
        self.is_dispatching = threading.Event()

    def start(self, runs: Optional[int] = None) -> None:
        self.reset_state()
        if runs is None:
            total_runs = None
        else:
            total_runs = multiprocessing.Value("i", runs)
        self.simulating_event_flag.set()
        self.processes = []

        # Can be updated to os.process_cpu_count() from 3.13
        for _ in range(os.cpu_count()):
            process = SimulationProcess(
                self.input,
                self.result_queue,
                self.simulation_type,
                self.simulating_event_flag,
                total_runs,
                batching=self.batching,
            )
            self.processes.append(process)
            process.start()

        self.is_dispatching.set()
        self.dispatcher = ResultDispatcher(
            self.result_queue, self.output, self.is_dispatching
        )
        self.dispatcher.start()

        if total_runs is not None:
            while True:
                runs_left = total_runs.value
                if runs_left <= 0:
                    self.stop()
                    break

    def stop(self) -> None:
        self.simulating_event_flag.clear()
        for p in self.processes:
            p.join()
        self.is_dispatching.clear()
        self.dispatcher.join()
        self.result_queue.close()
        self.result_queue.join_thread()


class Simulation:
    def __init__(self, input: int):
        self.input = input

    def run(self, *args, **kwargs) -> int:
        pass

    def start(self) -> Any:
        result = self.run()
        return result
