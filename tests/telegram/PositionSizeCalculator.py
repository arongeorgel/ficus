import unittest

from ficus.telegram.PositionSizeCalculator import PositionSizeCalculator


class TestPositionSizeCalculator(unittest.TestCase):
    def setUp(self):
        self.calculator = PositionSizeCalculator()
        self.account_size = 4000  # Example account balance in base currency
        self.risk_percentage = 2  # Risk 1% of account per trade
        self.stop_loss_pips = 50  # Example stop loss in pips

    def test_EURUSD(self):
        currency_pair = "EURUSD"
        expected_position_size = self.calculator.calculate_position_size(self.account_size, self.risk_percentage, self.stop_loss_pips, currency_pair)
        self.assertAlmostEqual(expected_position_size, 2.00, places=2)

    def test_USDJPY(self):
        currency_pair = "USDJPY"
        expected_position_size = self.calculator.calculate_position_size(self.account_size, self.risk_percentage, self.stop_loss_pips, currency_pair)
        self.assertAlmostEqual(expected_position_size, 200000.00, places=2)

    def test_GBPUSD(self):
        currency_pair = "GBPUSD"
        expected_position_size = self.calculator.calculate_position_size(self.account_size, self.risk_percentage, self.stop_loss_pips, currency_pair)
        self.assertAlmostEqual(expected_position_size, 2.00, places=2)

    def test_USDCHF(self):
        currency_pair = "USDCHF"
        expected_position_size = self.calculator.calculate_position_size(self.account_size, self.risk_percentage, self.stop_loss_pips, currency_pair)
        self.assertAlmostEqual(expected_position_size, 2.00, places=2)

    def test_AUDUSD(self):
        currency_pair = "AUDUSD"
        expected_position_size = self.calculator.calculate_position_size(self.account_size, self.risk_percentage, self.stop_loss_pips, currency_pair)
        self.assertAlmostEqual(expected_position_size, 2.00, places=2)

    def test_USDCAD(self):
        currency_pair = "USDCAD"
        expected_position_size = self.calculator.calculate_position_size(self.account_size, self.risk_percentage, self.stop_loss_pips, currency_pair)
        self.assertAlmostEqual(expected_position_size, 2.00, places=2)

    def test_NZDUSD(self):
        currency_pair = "NZDUSD"
        expected_position_size = self.calculator.calculate_position_size(self.account_size, self.risk_percentage, self.stop_loss_pips, currency_pair)
        self.assertAlmostEqual(expected_position_size, 2.00, places=2)

    def test_EURGBP(self):
        currency_pair = "EURGBP"
        expected_position_size = self.calculator.calculate_position_size(self.account_size, self.risk_percentage, self.stop_loss_pips, currency_pair)
        self.assertAlmostEqual(expected_position_size, 2.00, places=2)

    def test_EURJPY(self):
        currency_pair = "EURJPY"
        expected_position_size = self.calculator.calculate_position_size(self.account_size, self.risk_percentage, self.stop_loss_pips, currency_pair)
        self.assertAlmostEqual(expected_position_size, 200000.00, places=2)

    def test_GBPJPY(self):
        currency_pair = "GBPJPY"
        expected_position_size = self.calculator.calculate_position_size(self.account_size, self.risk_percentage, self.stop_loss_pips, currency_pair)
        self.assertAlmostEqual(expected_position_size, 200000.00, places=2)

    def test_AUDJPY(self):
        currency_pair = "AUDJPY"
        expected_position_size = self.calculator.calculate_position_size(self.account_size, self.risk_percentage, self.stop_loss_pips, currency_pair)
        self.assertAlmostEqual(expected_position_size, 200000.00, places=2)

    def test_EURAUD(self):
        currency_pair = "EURAUD"
        expected_position_size = self.calculator.calculate_position_size(self.account_size, self.risk_percentage, self.stop_loss_pips, currency_pair)
        self.assertAlmostEqual(expected_position_size, 2.00, places=2)

    def test_EURCHF(self):
        currency_pair = "EURCHF"
        expected_position_size = self.calculator.calculate_position_size(self.account_size, self.risk_percentage, self.stop_loss_pips, currency_pair)
        self.assertAlmostEqual(expected_position_size, 2.00, places=2)

    def test_AUDNZD(self):
        currency_pair = "AUDNZD"
        expected_position_size = self.calculator.calculate_position_size(self.account_size, self.risk_percentage, self.stop_loss_pips, currency_pair)
        self.assertAlmostEqual(expected_position_size, 2.00, places=2)

    def test_CADJPY(self):
        currency_pair = "CADJPY"
        expected_position_size = self.calculator.calculate_position_size(self.account_size, self.risk_percentage, self.stop_loss_pips, currency_pair)
        self.assertAlmostEqual(expected_position_size, 200000.00, places=2)

    def test_NZDJPY(self):
        currency_pair = "NZDJPY"
        expected_position_size = self.calculator.calculate_position_size(self.account_size, self.risk_percentage, self.stop_loss_pips, currency_pair)
        self.assertAlmostEqual(expected_position_size, 200000.00, places=2)

    def test_GBPCHF(self):
        currency_pair = "GBPCHF"
        expected_position_size = self.calculator.calculate_position_size(self.account_size, self.risk_percentage, self.stop_loss_pips, currency_pair)
        self.assertAlmostEqual(expected_position_size, 2.00, places=2)

    def test_GBPCAD(self):
        currency_pair = "GBPCAD"
        expected_position_size = self.calculator.calculate_position_size(self.account_size, self.risk_percentage, self.stop_loss_pips, currency_pair)
        self.assertAlmostEqual(expected_position_size, 2.00, places=2)

    def test_CHFJPY(self):
        currency_pair = "CHFJPY"
        expected_position_size = self.calculator.calculate_position_size(self.account_size, self.risk_percentage, self.stop_loss_pips, currency_pair)
        self.assertAlmostEqual(expected_position_size, 200000.00, places=2)

    def test_EURCAD(self):
        currency_pair = "EURCAD"
        expected_position_size = self.calculator.calculate_position_size(self.account_size, self.risk_percentage, self.stop_loss_pips, currency_pair)
        self.assertAlmostEqual(expected_position_size, 2.00, places=2)

    def test_GBPNZD(self):
        currency_pair = "GBPNZD"
        expected_position_size = self.calculator.calculate_position_size(self.account_size, self.risk_percentage, self.stop_loss_pips, currency_pair)
        self.assertAlmostEqual(expected_position_size, 2.00, places=2)

    def test_XAUUSD(self):
        currency_pair = "XAUUSD"
        pips = self.calculator.price_difference_in_pips(1800, 1808, currency_pair)
        expected_position_size = self.calculator.calculate_position_size(self.account_size, self.risk_percentage, currency_pair, pips)
        self.assertEqual(expected_position_size, 80)

if __name__ == "__main__":
    unittest.main()
