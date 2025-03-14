import unittest
from src.Output import MeanOutput
from src.ResultBatch import ResultBatch


class OutputTest(unittest.TestCase):
    pass

    # You can update the output and get the aggregate
    def test_get_aggregate(self):
        output = MeanOutput()
        output.update(10)
        output.update(12)
        result = output.aggregate()
        self.assertEqual(result, 11)

    def test_result_batch(self):
        output = MeanOutput()
        result_batch = ResultBatch([1, 2, 3, 4])
        output.update(result_batch)
        result = output.aggregate()
        self.assertEqual(result, 2.5)
