import unittest
from src.Output import MeanOutput
from src.ResultBatch import ResultBatch


class OutputTest(unittest.TestCase):
    # You can update the output and get the aggregate
    def test_get_aggregate(self):
        output = MeanOutput()
        output.update(ResultBatch(10, [10]))
        output.update(ResultBatch(10, [12]))
        result = output.aggregate()
        self.assertEqual(result, 11)

    def test_result_batch(self):
        output = MeanOutput()
        result_batch = ResultBatch(10, [1, 2, 3, 4])
        output.update(result_batch)
        result = output.aggregate()
        self.assertEqual(result, 2.5)

    def test_default_input(self):
        output = MeanOutput()
        output.update(ResultBatch(10, [100]))
        output.update(ResultBatch(12, [200]))
        result = output.aggregate()
        self.assertEqual(result, 200)

    def test_change_input(self):
        output = MeanOutput()
        output.update(ResultBatch(10, [100]))
        output.update(ResultBatch(12, [200]))
        output.set_input(10)
        result = output.aggregate()
        self.assertEqual(result, 100)
