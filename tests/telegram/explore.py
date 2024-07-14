import unittest
from unittest.mock import patch, MagicMock

from ficus.telegram.telegram_messages import parse_trade_message, execute_trade, handle_message

CHAT_ID="123"


class TestTradeParser(unittest.TestCase):

    def test_parse_trade_message(self):
        message = """XAUUSD buy now
            Enter 2304
            SL 2296
            TP1 2307
            TP2 2312
            TP3 2315
            TP4 2337"""
        expected = {
            'action': 'buy',
            'symbol': 'XAUUSD',
            'entry': 2304.0,
            'sl': 2296.0,
            'tps': [2307.0, 2312.0, 2315.0, 2337.0]
        }
        self.assertEqual(parse_trade_message(message), expected)

    def test_parse_trade_message_sell(self):
        message = """XAUUSD sell now
            Enter 2304
            SL 2312
            TP1 2300
            TP2 2295
            TP3 2290
            TP4 2280"""
        expected = {
            'action': 'sell',
            'symbol': 'XAUUSD',
            'entry': 2304.0,
            'sl': 2312.0,
            'tps': [2300.0, 2295.0, 2290.0, 2280.0]
        }
        self.assertEqual(parse_trade_message(message), expected)

    def test_execute_trade_incomplete_data(self):
        trade = {'action': 'buy', 'symbol': 'XAUUSD', 'entry': 2304.0, 'sl': None, 'tps': [2307.0, 2312.0, 2315.0, 2337.0]}
        self.assertIsNone(execute_trade(trade))

    @patch('MetaTrader5.positions_get')
    @patch('MetaTrader5.order_send')
    def test_close_tp_messages(self, mock_order_send, mock_positions_get, mt5=None):
        positions = [
            MagicMock(ticket=1, symbol="XAUUSD", type=mt5.ORDER_TYPE_BUY, volume=0.16, price_open=2304.0),
            MagicMock(ticket=2, symbol="EURUSD", type=mt5.ORDER_TYPE_BUY, volume=0.16, price_open=1.1000),
            MagicMock(ticket=3, symbol="GBPUSD", type=mt5.ORDER_TYPE_SELL, volume=0.16, price_open=1.3000),
            MagicMock(ticket=4, symbol="USDJPY", type=mt5.ORDER_TYPE_SELL, volume=0.16, price_open=110.0)
        ]
        mock_positions_get.return_value = positions

        update = MagicMock()
        context = MagicMock()
        update.message.chat_id = CHAT_ID
        update.message.text = "Close TP1"
        update.message.reply_to_message.text = "XAUUSD buy now\nEnter 2304\nSL 2296\nTP1 2307\nTP2 2312\nTP3 2315\nTP4 2337"

        handle_message(update, context)

        update.message.text = "Close TP2"
        update.message.reply_to_message.text = "EURUSD buy now\nEnter 1.1000\nSL 1.0900\nTP1 1.1050\nTP2 1.1100\nTP3 1.1150\nTP4 1.1200"
        handle_message(update, context)

        update.message.text = "Close TP3"
        update.message.reply_to_message.text = "GBPUSD sell now\nEnter 1.3000\nSL 1.3100\nTP1 1.2950\nTP2 1.2900\nTP3 1.2850\nTP4 1.2800"
        handle_message(update, context)

        update.message.text = "Close TP4"
        update.message.reply_to_message.text = "USDJPY sell now\nEnter 110.0\nSL 111.0\nTP1 109.5\nTP2 109.0\nTP3 108.5\nTP4 108.0"
        handle_message(update, context)

        self.assertEqual(mock_order_send.call_count, 4)

    @patch('MetaTrader5.positions_get')
    @patch('MetaTrader5.order_send')
    def test_sl_entry_message(self, mock_order_send, mock_positions_get, mt5=None):
        positions = [
            MagicMock(ticket=1, symbol="XAUUSD", type=mt5.ORDER_TYPE_BUY, volume=0.16, price_open=2304.0),
        ]
        mock_positions_get.return_value = positions

        update = MagicMock()
        context = MagicMock()
        update.message.chat_id = CHAT_ID
        update.message.text = "SL entry"
        update.message.reply_to_message.text = "XAUUSD buy now\nEnter 2304\nSL 2296\nTP1 2307\nTP2 2312\nTP3 2315\nTP4 2337"

        handle_message(update, context)

        modify_request = {
            'action': mt5.TRADE_ACTION_SLTP,
            'position': positions[0].ticket,
            'sl': positions[0].price_open,
        }
        mock_order_send.assert_called_with(modify_request)

if __name__ == '__main__':
    unittest.main()
