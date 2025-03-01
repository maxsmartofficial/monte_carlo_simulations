import unittest
from src.Output import MeanOutput

class OutputTest(unittest.TestCase):
    pass
    # You can update the output and get the aggregate
    def test_get_aggregate(self):
        output = MeanOutput()
        output.update(10)
        output.update(12)
        result = output.aggregate()
        self.assertEqual(result, 11)

    
    



