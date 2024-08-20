import unittest

from ficus.models.models import TradingSymbol, TradeDirection


class TestCalculateLevels(unittest.TestCase):

    def test_xauusd_buy(self):
        entry_price = 1300.00
        symbol = TradingSymbol.XAUUSD
        direction = TradeDirection.BUY

        expected_sl = 1297.00
        expected_tp1 = 1303.00
        expected_tp2 = 1305.00
        expected_tp3 = 1310.00
        expected_volume = 0.27  # Based on max_risk / sl_difference / contract_size

        sl, tp1, tp2, tp3, volume = TradingSymbol.calculate_levels(symbol, entry_price, direction, 0)

        self.assertAlmostEqual(sl, expected_sl, places=2,
                               msg="Stop Loss calculation for XAUUSD buy is incorrect")
        self.assertAlmostEqual(tp1, expected_tp1, places=2,
                               msg="Take Profit 1 calculation for XAUUSD buy is incorrect")
        self.assertAlmostEqual(tp2, expected_tp2, places=2,
                               msg="Take Profit 2 calculation for XAUUSD buy is incorrect")
        self.assertAlmostEqual(tp3, expected_tp3, places=2,
                               msg="Take Profit 3 calculation for XAUUSD buy is incorrect")
        self.assertAlmostEqual(volume, expected_volume, places=2, msg="Volume calculation for XAUUSD buy is incorrect")

    def test_xauusd_sell(self):
        entry_price = 1300.00
        symbol = TradingSymbol.XAUUSD
        direction = TradeDirection.SELL

        expected_sl = 1303.00
        expected_tp1 = 1297.00
        expected_tp2 = 1295.00
        expected_tp3 = 1290.00
        expected_volume = 0.27  # Based on max_risk / sl_difference / contract_size

        sl, tp1, tp2, tp3, volume = TradingSymbol.calculate_levels(symbol, entry_price, direction, 0)

        self.assertAlmostEqual(sl, expected_sl, places=2,
                               msg="Stop Loss calculation for XAUUSD sell is incorrect")
        self.assertAlmostEqual(tp1, expected_tp1, places=2,
                               msg="Take Profit 1 calculation for XAUUSD sell is incorrect")
        self.assertAlmostEqual(tp2, expected_tp2, places=2,
                               msg="Take Profit 2 calculation for XAUUSD sell is incorrect")
        self.assertAlmostEqual(tp3, expected_tp3, places=2,
                               msg="Take Profit 3 calculation for XAUUSD sell is incorrect")
        self.assertAlmostEqual(volume, expected_volume, places=2, msg="Volume calculation for XAUUSD sell is incorrect")

    def test_btc_buy(self):
        entry_price = 30000.00
        symbol = TradingSymbol.BTCUSD
        direction = TradeDirection.BUY

        expected_sl = 29700.00
        expected_tp1 = 30300.00
        expected_tp2 = 30500.00
        expected_tp3 = 31000.00
        expected_volume = 0.27  # Based on max_risk / sl_difference / contract_size

        sl, tp1, tp2, tp3, volume = TradingSymbol.calculate_levels(symbol, entry_price, direction, 0)

        self.assertAlmostEqual(sl, expected_sl, places=2,
                               msg="Stop Loss calculation for BTC buy is incorrect")
        self.assertAlmostEqual(tp1, expected_tp1, places=2,
                               msg="Take Profit 1 calculation for BTC buy is incorrect")
        self.assertAlmostEqual(tp2, expected_tp2, places=2,
                               msg="Take Profit 2 calculation for BTC buy is incorrect")
        self.assertAlmostEqual(tp3, expected_tp3, places=2,
                               msg="Take Profit 3 calculation for BTC buy is incorrect")
        self.assertAlmostEqual(volume, expected_volume, places=2, msg="Volume calculation for BTC buy is incorrect")

    def test_btc_sell(self):
        entry_price = 30000.00
        symbol = TradingSymbol.BTCUSD
        direction = TradeDirection.SELL

        expected_sl = 30300.00
        expected_tp1 = 29700.00
        expected_tp2 = 29500.00
        expected_tp3 = 29000.00
        expected_volume = 0.27  # Based on max_risk / sl_difference / contract_size

        sl, tp1, tp2, tp3, volume = TradingSymbol.calculate_levels(symbol, entry_price, direction, 0)

        self.assertAlmostEqual(sl, expected_sl, places=2,
                               msg="Stop Loss calculation for BTC sell is incorrect")
        self.assertAlmostEqual(tp1, expected_tp1, places=2,
                               msg="Take Profit 1 calculation for BTC sell is incorrect")
        self.assertAlmostEqual(tp2, expected_tp2, places=2,
                               msg="Take Profit 2 calculation for BTC sell is incorrect")
        self.assertAlmostEqual(tp3, expected_tp3, places=2,
                               msg="Take Profit 3 calculation for BTC sell is incorrect")
        self.assertAlmostEqual(volume, expected_volume, places=2, msg="Volume calculation for BTC sell is incorrect")

    def test_eurusd_buy(self):
        entry_price = 1.08
        symbol = TradingSymbol.EURUSD
        direction = TradeDirection.BUY

        expected_sl = 1.076
        expected_tp1 = 1.084
        expected_tp2 = 1.087
        expected_tp3 = 1.092
        expected_volume = 0.2  # Based on max_risk / sl_difference / contract_size

        sl, tp1, tp2, tp3, volume = TradingSymbol.calculate_levels(symbol, entry_price, direction, 0)

        self.assertAlmostEqual(sl, expected_sl, places=4,
                               msg="Stop Loss calculation for EURUSD buy is incorrect")
        self.assertAlmostEqual(tp1, expected_tp1, places=4,
                               msg="Take Profit 1 calculation for EURUSD buy is incorrect")
        self.assertAlmostEqual(tp2, expected_tp2, places=4,
                               msg="Take Profit 2 calculation for EURUSD buy is incorrect")
        self.assertAlmostEqual(tp3, expected_tp3, places=4,
                               msg="Take Profit 3 calculation for EURUSD buy is incorrect")
        self.assertAlmostEqual(volume, expected_volume, places=4, msg="Volume calculation for EURUSD buy is incorrect")

    def test_eurusd_sell(self):
        entry_price = 1.08370
        symbol = TradingSymbol.EURUSD
        direction = TradeDirection.SELL

        expected_sl = 1.08770
        expected_tp1 = 1.0797
        expected_tp2 = 1.0767
        expected_tp3 = 1.0717
        expected_volume = 0.2  # Based on max_risk / sl_difference / contract_size

        sl, tp1, tp2, tp3, volume = TradingSymbol.calculate_levels(symbol, entry_price, direction, 0)

        self.assertAlmostEqual(sl, expected_sl, places=4,
                               msg="Stop Loss calculation for EURUSD sell is incorrect")
        self.assertAlmostEqual(tp1, expected_tp1, places=4,
                               msg="Take Profit 1 calculation for EURUSD sell is incorrect")
        self.assertAlmostEqual(tp2, expected_tp2, places=4,
                               msg="Take Profit 2 calculation for EURUSD sell is incorrect")
        self.assertAlmostEqual(tp3, expected_tp3, places=4,
                               msg="Take Profit 3 calculation for EURUSD sell is incorrect")
        self.assertAlmostEqual(volume, expected_volume, places=4, msg="Volume calculation for EURUSD sell is incorrect")
