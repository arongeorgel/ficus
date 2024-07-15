import unittest
from unittest.mock import Mock, patch
from ficus.metatrader.__main__ import start_monitoring_trades


class TestStartMonitoringTrades(unittest.TestCase):

    # Mock MetatraderTerminal class
    MetatraderTerminal = Mock()

    @patch('ficus.metatrader.__main__.start_monitoring_trades', autospec=True)
    @patch('ficus.metatrader.__main__.validate_price', autospec=True)
    def test_start_monitoring_trades(self, mock_start_monitoring_trades, mock_validate_price):
        # Define return values for mocked function calls
        self.MetatraderTerminal.get_open_positions.return_value = [Mock()]
        self.MetatraderTerminal.get_current_price.return_value = 1.2345
        mock_validate_price.return_value = Mock()

        # Call function to be tested
        start_monitoring_trades()

        # Asserts
        self.MetatraderTerminal.get_open_positions.assert_called_once()
        self.MetatraderTerminal.get_current_price.assert_called_once()
        mock_validate_price.assert_called_once()

    @patch('ficus.metatrader.__main__.start_monitoring_trades', autospec=True)
    @patch('ficus.metatrader.__main__.validate_price', autospec=True)
    def test_start_monitoring_trades_no_positions(self, mock_start_monitoring_trades, mock_validate_price):
        # If no positions are open, function should not call more
        self.MetatraderTerminal.get_open_positions.return_value = None

        # Call function to be tested
        start_monitoring_trades()

        # Asserts
        self.MetatraderTerminal.get_open_positions.assert_called_once()
        self.MetatraderTerminal.get_current_price.assert_not_called()
        mock_validate_price.assert_not_called()


if __name__ == "__main__":
    unittest.main()
