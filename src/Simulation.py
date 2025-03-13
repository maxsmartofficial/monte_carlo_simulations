import multiprocessing
import threading
import os
from dataclasses import dataclass


@dataclass
class ResultBatch:
    batch: list


class ResultDispatcher(threading.Thread):
    def __init__(self, result_queue, output, is_dispatching, *args, **kwargs):
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
    batch_size = 10

    def __init__(
        self,
        input,
        result_queue,
        simulation_type,
        simulating,
        total_runs=None,
        batching=False,
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

    def run(self):
        while self.simulating.is_set():
            if self.total_runs is not None:
                with self.total_runs.get_lock():
                    if self.total_runs.value <= 0:
                        break
                    else:
                        self.total_runs.value -= 1

            simulation = self.simulation_type(self.input)
            result = simulation.start()
            if self.batching:
                self.batch.append(result)
                if len(self.batch) == self.batch_size:
                    batch = ResultBatch(self.batch)
                    self.result_queue.put(batch)
                    self.batch = []
            else:
                self.result_queue.put(result)


class SimulationManager:
    def __init__(self, input, simulation_type, output, batching=True):
        self.input = input
        self.simulation_type = simulation_type
        self.output = output
        self.batching = batching

    def _run_simulation_process(self):
        simulation = Simulation(self.input)
        result = simulation.start()

        return result

    def reset_state(self):
        self.result_queue = multiprocessing.Queue()
        self.simulating_event_flag = multiprocessing.Event()
        self.is_dispatching = threading.Event()

    def start(self, runs=None):
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

    def stop(self):
        self.simulating_event_flag.clear()
        for p in self.processes:
            p.join()
        self.is_dispatching.clear()
        self.dispatcher.join()
        self.result_queue.close()
        self.result_queue.join_thread()


class Simulation:
    def __init__(self, input):
        self.input = input

    def run(self, *args, **kwargs):
        pass

    def start(self):
        result = self.run()
        return result
