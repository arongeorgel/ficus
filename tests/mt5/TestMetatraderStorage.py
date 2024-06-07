import unittest
from unittest.mock import patch, mock_open, call
from datetime import datetime, timedelta
import json
import os
import pandas as pd
from metaapi_cloud_sdk.metaapi.models import MetatraderSymbolPrice

from ficus.mt5.MetatraderStorage import MetatraderSymbolPriceManager
from ficus.mt5.models import TradingSymbol


class TestMetatraderSymbolPriceManager(unittest.TestCase):
    def setUp(self):
        self.trading_symbol = TradingSymbol.XAUUSD  # Adjust this according to your actual enum
        self.manager = MetatraderSymbolPriceManager(self.trading_symbol)

    @patch('builtins.open', new_callable=mock_open, read_data='[]')
    def test_load_data(self, mock_file):
        manager = MetatraderSymbolPriceManager(self.trading_symbol)
        timestamp = datetime.now().strftime("%Y_%m_%d")
        yesterday_timestamp = (datetime.now() - timedelta(days=1)).strftime("%Y_%m_%d")
        expected_calls = [
            call(f"meta_symbol_xauusd_{timestamp}.json", 'r'),
            call(f"meta_symbol_xauusd_{yesterday_timestamp}.json", 'r')
        ]
        mock_file.assert_has_calls(expected_calls, any_order=True)
        self.assertEqual(manager.data, [])

    @patch('builtins.open', new_callable=mock_open)
    def test_load_data_with_content(self, mock_file):
        # Mock today's file with data and yesterday's file as empty
        today_data = json.dumps([
            {"symbol": "XAUUSD", "bid": 1800.5, "brokerTime": "2023-06-01T12:00:00", "time": "2023-06-01T12:00:00"}
        ])
        mock_file.side_effect = [
            mock_open(read_data=today_data).return_value,
            mock_open(read_data='[]').return_value
        ]

        manager = MetatraderSymbolPriceManager(self.trading_symbol)
        timestamp = datetime.now().strftime("%Y_%m_%d")
        yesterday_timestamp = (datetime.now() - timedelta(days=1)).strftime("%Y_%m_%d")

        expected_calls = [
            call(f"meta_symbol_xauusd_{timestamp}.json", 'r'),
            call(f"meta_symbol_xauusd_{yesterday_timestamp}.json", 'r')
        ]
        mock_file.assert_has_calls(expected_calls, any_order=True)
        self.assertEqual(len(manager.data), 1)
        self.assertEqual(manager.data[0]['bid'], 1800.5)

    @patch('builtins.open', new_callable=mock_open)
    def test_load_data_with_content_in_both_files(self, mock_file):
        # Mock today's and yesterday's files with data
        today_data = json.dumps([
            {"symbol": "XAUUSD", "bid": 1800.5, "brokerTime": "2023-06-02T12:00:00", "time": "2023-06-02T12:00:00"}
        ])
        yesterday_data = json.dumps([
            {"symbol": "XAUUSD", "bid": 1799.5, "brokerTime": "2023-06-01T12:00:00", "time": "2023-06-01T12:00:00"}
        ])
        mock_file.side_effect = [
            mock_open(read_data=today_data).return_value,
            mock_open(read_data=yesterday_data).return_value
        ]

        manager = MetatraderSymbolPriceManager(self.trading_symbol)
        timestamp = datetime.now().strftime("%Y_%m_%d")
        yesterday_timestamp = (datetime.now() - timedelta(days=1)).strftime("%Y_%m_%d")

        expected_calls = [
            call(f"meta_symbol_xauusd_{timestamp}.json", 'r'),
            call(f"meta_symbol_xauusd_{yesterday_timestamp}.json", 'r')
        ]
        mock_file.assert_has_calls(expected_calls, any_order=True)
        self.assertEqual(len(manager.data), 2)
        self.assertEqual(manager.data[0]['bid'], 1800.5)
        self.assertEqual(manager.data[1]['bid'], 1799.5)

    @patch('builtins.open', new_callable=mock_open)
    def test_save_data(self, mock_file):
        symbol_price = {
            "symbol": "XAUUSD",
            "bid": 1800.5,
            "brokerTime": datetime.now(),
            "time": datetime.now()
        }
        self.manager.data.append(symbol_price)
        self.manager.save_data()

        file_path = f"meta_symbol_xauusd_{datetime.now().strftime('%Y_%m_%d')}.json"
        mock_file.assert_called_once_with(file_path, 'w')

        handle = mock_file()
        written_content = "".join(c.args[0] for c in handle.write.call_args_list)

        json_data = [self.manager._convert_datetime_to_str(symbol_price)]
        expected_content = json.dumps(json_data, indent=4)

        self.assertEqual(written_content, expected_content)

    def test_add_symbol_price(self):
        symbol_price = MetatraderSymbolPrice(
            symbol='XAUUSD',
            bid=1800.5,
            brokerTime=datetime.now().strftime("YYYY-MM-DD HH:mm:ss.SSS"),
            time=datetime.now(),
            ask=1801.5,
            lossTickValue=0.1,
            profitTickValue=0.1,
            equity=87000,
            accountCurrencyExchangeRate=1
        )
        with patch('builtins.open', mock_open()) as mock_file:
            self.manager.add_symbol_price(symbol_price)
            file_path = f"meta_symbol_xauusd_{datetime.now().strftime('%Y_%m_%d')}.json"
            mock_file.assert_called_with(file_path, 'w')
            self.assertIn(symbol_price, self.manager.data)

    def test_convert_datetime_to_str(self):
        symbol_price = {
            "symbol": "XAUUSD",
            "price": 1800.5,
            "brokerTime": datetime.now(),
            "time": datetime.now()
        }
        result = self.manager._convert_datetime_to_str(symbol_price)
        self.assertIsInstance(result['brokerTime'], str)
        self.assertIsInstance(result['time'], str)

    def test_convert_str_to_datetime(self):
        symbol_price = {
            "symbol": "XAUUSD",
            "price": 1800.5,
            "brokerTime": datetime.now().isoformat(),
            "time": datetime.now().isoformat()
        }
        result = self.manager._convert_str_to_datetime(symbol_price)
        self.assertIsInstance(result['brokerTime'], datetime)
        self.assertIsInstance(result['time'], datetime)

    def test_remove_old_data(self):
        old_time = datetime.now() - timedelta(hours=49)
        new_time = datetime.now() - timedelta(hours=47)
        self.manager.data = [
            {"symbol": "XAUUSD", "price": 1800.5, "brokerTime": old_time, "time": old_time},
            {"symbol": "XAUUSD", "price": 1800.5, "brokerTime": new_time, "time": new_time}
        ]
        self.manager.remove_old_data()
        self.assertEqual(len(self.manager.data), 1)
        self.assertEqual(self.manager.data[0]['brokerTime'], new_time)

    def test_remove_old_data_all_new(self):
        new_time_1 = datetime.now() - timedelta(hours=47)
        new_time_2 = datetime.now() - timedelta(hours=46)
        self.manager.data = [
            {"symbol": "XAUUSD", "price": 1800.5, "brokerTime": new_time_1, "time": new_time_1},
            {"symbol": "XAUUSD", "price": 1800.5, "brokerTime": new_time_2, "time": new_time_2}
        ]
        self.manager.remove_old_data()
        self.assertEqual(len(self.manager.data), 2)

    def test_generate_ohlcv(self):
        current_time = datetime.now()
        self.manager.data = [
            {"symbol": "XAUUSD", "price": 1800.5, "brokerTime": current_time - timedelta(minutes=10),
             "time": current_time - timedelta(minutes=10), "bid": 1800.5},
            {"symbol": "XAUUSD", "price": 1801.5, "brokerTime": current_time - timedelta(minutes=5),
             "time": current_time - timedelta(minutes=5), "bid": 1801.5},
            {"symbol": "XAUUSD", "price": 1802.5, "brokerTime": current_time, "time": current_time, "bid": 1802.5}
        ]
        result = self.manager.generate_ohlcv(5)
        self.assertEqual(len(result), 3)  # Assuming we have 3 intervals in the data
        self.assertIn('Open', result.columns)
        self.assertIn('High', result.columns)
        self.assertIn('Low', result.columns)
        self.assertIn('Close', result.columns)

    def test_generate_ohlcv_different_intervals(self):
        current_time = datetime.now()
        self.manager.data = [
            {"symbol": "XAUUSD", "price": 1800.5, "brokerTime": current_time - timedelta(minutes=10),
             "time": current_time - timedelta(minutes=10), "bid": 1800.5},
            {"symbol": "XAUUSD", "price": 1801.5, "brokerTime": current_time - timedelta(minutes=5),
             "time": current_time - timedelta(minutes=5), "bid": 1801.5},
            {"symbol": "XAUUSD", "price": 1802.5, "brokerTime": current_time, "time": current_time, "bid": 1802.5}
        ]
        result_5min = self.manager.generate_ohlcv(5)
        self.assertEqual(len(result_5min), 3)  # Assuming we have 3 intervals in the data

        result_10min = self.manager.generate_ohlcv(10)
        self.assertEqual(len(result_10min), 2)  # Assuming we have 2 intervals in the data


if __name__ == '__main__':
    unittest.main()
