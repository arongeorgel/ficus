import unittest
from ficus.signals.PositionSizeCalculator import PositionSizeCalculator


class TestPositionSizeCalculator(unittest.TestCase):
    
    def setUp(self):
        self.calculator = PositionSizeCalculator()

    def test_ti(self):
        self.assertIsInstance(self.calculator, PositionSizeCalculator)

    def test_forex_calculator(self):
        symbol = "AUDUSD"
        entry = 1.4
        sl = 1.35
        account_balance = 5000
        risk_percentage = 5

        returned_lots = self.calculator.forex_calculator(symbol, entry, sl, account_balance, risk_percentage, 0)
        
        self.assertIsNotNone(returned_lots)
        self.assertIsInstance(returned_lots, float)

    def test_forex_calculator_none(self):
        symbol = "AUDNZD"
        entry = 1.1
        sl = 1.05
        account_balance = 7500
        risk_percentage = 10

        returned_lots = self.calculator.forex_calculator(symbol, entry, sl, account_balance, risk_percentage, 1)

        self.assertIsNone(returned_lots)

if __name__ == '__main__':
    unittest.main()