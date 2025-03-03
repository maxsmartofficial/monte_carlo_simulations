import multiprocessing
import threading
import os


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
    def __init__(
        self,
        input,
        result_queue,
        simulation_type,
        simulating,
        total_runs,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.input = input
        self.result_queue = result_queue
        self.simulation_type = simulation_type
        self.simulating = simulating
        self.total_runs = total_runs

    def run(self):
        while self.simulating.is_set():
            with self.total_runs.get_lock():
                if self.total_runs.value <= 0:
                    break
                else:
                    self.total_runs.value -= 1

            simulation = self.simulation_type(self.input)
            result = simulation.start()
            self.result_queue.put(result)


class SimulationManager:
    def __init__(self, input, simulation_type, output):
        self.input = input
        self.simulation_type = simulation_type
        self.output = output

    def _run_simulation_process(self):
        simulation = Simulation(self.input)
        result = simulation.start()

        return result

    def start(self, runs=None):
        result_queue = multiprocessing.Queue()
        total_runs = multiprocessing.Value("i", runs)
        simulating_event_flag = multiprocessing.Event()
        simulating_event_flag.set()
        processes = []

        for _ in range(
            os.cpu_count()
        ):  # Can be updated to os.process_cpu_count() from 3.13
            process = SimulationProcess(
                self.input,
                result_queue,
                self.simulation_type,
                simulating_event_flag,
                total_runs,
            )
            processes.append(process)
            process.start()

        is_dispatching = threading.Event()
        is_dispatching.set()
        dispatcher = ResultDispatcher(result_queue, self.output, is_dispatching)
        dispatcher.start()

        while True:
            runs_left = (
                total_runs.value
            )  # We don't need a lock, since we just need the value
            if runs_left <= 0:
                # Shut down everything
                simulating_event_flag.clear()
                # Check all simulations have finished
                for p in processes:
                    p.join()
                # Check all results have been dispatched
                result_queue.close()
                result_queue.join_thread()
                # Stop the dispatcher
                is_dispatching.clear()
                dispatcher.join()
                break

    def stop(self):
        pass


class Simulation:
    def __init__(self, input):
        self.input = input

    def run(self, *args, **kwargs):
        pass

    def start(self):
        result = self.run()
        return result
