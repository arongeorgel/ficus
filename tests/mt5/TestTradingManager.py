import unittest
from abc import ABC
from unittest.mock import AsyncMock

from ficus.mt5.TradingManager import TradingManager
from ficus.mt5.listeners.ITradingCallback import ITradingCallback
from ficus.mt5.models import TradeDirection, FicusTrade, TradingSymbol


class ITradingCallbackMock(ITradingCallback, ABC):
    async def close_trade(self, trade: FicusTrade, symbol: str):
        pass

    async def partially_close_trade(self, trade: FicusTrade, symbol: str):
        pass

    async def modify_trade(self, trade: FicusTrade):
        pass

    async def open_trade(self, symbol: str, direction: TradeDirection, volume: float, stop_loss):
        return {'positionId': '12345'}


class MockSynchronizationListener:
    def __init__(self, manager):
        self.manager = manager

    async def simulate_price_change(self, trading_symbol, price):
        await self.manager.validate_price(price, trading_symbol)

    async def simulate_ohlcv_change(self, series):
        await self.manager.on_ohclv(series)


class TestTradingManager(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.callback_mock = ITradingCallbackMock()
        self.callback_mock.close_trade = AsyncMock()
        self.callback_mock.partially_close_trade = AsyncMock()
        self.callback_mock.modify_trade = AsyncMock()
        self.callback_mock.open_trade = AsyncMock(return_value={'positionId': '12345'})

        self.trading_manager = TradingManager(self.callback_mock)
        self.listener = MockSynchronizationListener(self.trading_manager)

        self.test_entry_price = 1300
        self.test_symbol = TradingSymbol.XAUUSD

        self.test_expected_sell_sl = 1303
        self.test_expected_sell_sl_tp1_hit = 1301.5
        self.test_expected_sell_tp = (1297, 1295, 1290)

        self.test_expected_buy_sl = 1297.00
        self.test_expected_buy_sl_tp1_hit = 1298.5
        self.test_expected_buy_tp = (1303, 1305, 1310)

        self.test_expected_tp_hits = [False, False, False]
        self.test_expected_volume = 0.27
        self.test_expected_tp1_volume = 0.14
        self.test_expected_tp2_volume = 0.09

        print('=== START ===')

    async def test_open_trade_buy(self):
        await self.trading_manager._open_trade(TradeDirection.BUY, self.test_symbol, self.test_entry_price)

        self.assertIn(self.test_symbol, self.trading_manager._current_trades)
        trade = self.trading_manager._current_trades[self.test_symbol]
        self.assertEqual(trade['position'], TradeDirection.BUY)
        self.assertEqual(trade['volume'], self.test_expected_volume)
        self.assertEqual(trade['start_volume'], self.test_expected_volume)
        self.assertEqual(trade['stop_loss_price'], self.test_expected_buy_sl)
        self.assertEqual(trade['take_profits'], self.test_expected_buy_tp)
        self.assertEqual(trade['take_profits_hit'], self.test_expected_tp_hits)

    async def test_open_trade_sell(self):
        await self.trading_manager._open_trade(TradeDirection.SELL, self.test_symbol, self.test_entry_price)

        self.assertIn(self.test_symbol, self.trading_manager._current_trades)
        trade = self.trading_manager._current_trades[self.test_symbol]
        self.assertEqual(trade['position'], TradeDirection.SELL)
        self.assertEqual(trade['volume'], self.test_expected_volume)
        self.assertEqual(trade['start_volume'], self.test_expected_volume)

        self.assertEqual(trade['stop_loss_price'], self.test_expected_sell_sl)
        self.assertEqual(trade['take_profits'], self.test_expected_sell_tp)
        self.assertEqual(trade['take_profits_hit'], self.test_expected_tp_hits)

    async def test_close_trade(self):
        await self.trading_manager._open_trade(TradeDirection.BUY, self.test_symbol, self.test_entry_price)
        await self.listener.simulate_price_change(self.test_symbol, 1296)  # Trigger SL

        self.assertNotIn(self.test_symbol, self.trading_manager._current_trades)
        self.callback_mock.close_trade.assert_called()

    async def test_take_profit_levels(self):
        await self.trading_manager._open_trade(TradeDirection.BUY, self.test_symbol, self.test_entry_price)
        self.callback_mock.open_trade.assert_called()
        trade = self.trading_manager._current_trades[self.test_symbol]

        # Hit TP1
        await self.listener.simulate_price_change(self.test_symbol, 1304)
        self.assertEqual(trade['volume'], self.test_expected_tp1_volume)
        self.assertEqual(trade['take_profits_hit'], [True, False, False])
        self.callback_mock.partially_close_trade.assert_called()

        self.assertEqual(trade['stop_loss_price'], self.test_expected_buy_sl_tp1_hit)
        self.callback_mock.modify_trade.assert_called()

        self.assertEqual(trade['position'], TradeDirection.BUY)
        self.assertEqual(trade['start_volume'], self.test_expected_volume)
        self.assertEqual(trade['take_profits'], self.test_expected_buy_tp)

        # Hit TP2
        await self.listener.simulate_price_change(self.test_symbol, 1305)
        self.assertEqual(trade['volume'], self.test_expected_tp2_volume)
        self.assertEqual(trade['take_profits_hit'], [True, True, False])
        self.callback_mock.partially_close_trade.assert_called()

        self.assertEqual(trade['stop_loss_price'], self.test_entry_price)
        self.callback_mock.modify_trade.assert_called()

        self.assertEqual(trade['position'], TradeDirection.BUY)
        self.assertEqual(trade['start_volume'], self.test_expected_volume)
        self.assertEqual(trade['take_profits'], self.test_expected_buy_tp)

        # Hit TP3
        await self.listener.simulate_price_change(self.test_symbol, 1311)
        self.assertEqual(trade['take_profits_hit'], [True, True, True])
        self.assertNotIn(self.test_symbol, self.trading_manager._current_trades)
        self.callback_mock.close_trade.assert_called()

    async def test_price_fluctuation(self):
        await self.trading_manager._open_trade(TradeDirection.BUY, self.test_symbol, self.test_entry_price)
        self.assertIn(self.test_symbol, self.trading_manager._current_trades)
        self.callback_mock.open_trade.assert_called()

        trade = self.trading_manager._current_trades[self.test_symbol]

        # Hit TP1
        await self.listener.simulate_price_change(self.test_symbol, 1304)
        self.assertEqual(trade['volume'], self.test_expected_tp1_volume)
        self.assertEqual(trade['take_profits_hit'], [True, False, False])
        self.callback_mock.partially_close_trade.assert_called()

        self.callback_mock.modify_trade.assert_called()
        self.assertEqual(trade['stop_loss_price'], self.test_expected_buy_sl_tp1_hit)

        self.assertEqual(trade['position'], TradeDirection.BUY)
        self.assertEqual(trade['start_volume'], self.test_expected_volume)
        self.assertEqual(trade['take_profits'], self.test_expected_buy_tp)

        # Price drops but no SL hit
        await self.listener.simulate_price_change(self.test_symbol, 1302.5)
        self.assertEqual(trade['volume'], self.test_expected_tp1_volume)
        self.assertEqual(trade['take_profits_hit'], [True, False, False])
        self.assertEqual(trade['stop_loss_price'], self.test_expected_buy_sl_tp1_hit)
        self.assertEqual(trade['position'], TradeDirection.BUY)
        self.assertEqual(trade['start_volume'], self.test_expected_volume)
        self.assertEqual(trade['take_profits'], self.test_expected_buy_tp)

        # Hit TP2
        await self.listener.simulate_price_change(self.test_symbol, 1305)
        self.assertEqual(trade['volume'], self.test_expected_tp2_volume)
        self.assertEqual(trade['take_profits_hit'], [True, True, False])
        self.callback_mock.partially_close_trade.assert_called()

        self.callback_mock.modify_trade.assert_called()
        self.assertEqual(trade['stop_loss_price'], self.test_entry_price)

        self.assertEqual(trade['position'], TradeDirection.BUY)
        self.assertEqual(trade['start_volume'], self.test_expected_volume)
        self.assertEqual(trade['take_profits'], self.test_expected_buy_tp)

    async def test_take_profit_1_and_stop_loss(self):
        await self.trading_manager._open_trade(TradeDirection.BUY, self.test_symbol, self.test_entry_price)
        trade = self.trading_manager._current_trades[self.test_symbol]

        # Hit TP1
        await self.listener.simulate_price_change(self.test_symbol, 1304)
        self.assertEqual(trade['volume'], self.test_expected_tp1_volume)
        self.assertEqual(trade['take_profits_hit'], [True, False, False])
        self.callback_mock.partially_close_trade.assert_called()

        self.callback_mock.modify_trade.assert_called()
        self.assertEqual(trade['stop_loss_price'], self.test_expected_buy_sl_tp1_hit)

        self.assertEqual(trade['position'], TradeDirection.BUY)
        self.assertEqual(trade['start_volume'], self.test_expected_volume)
        self.assertEqual(trade['take_profits'], self.test_expected_buy_tp)

        # Hit SL
        await self.listener.simulate_price_change(self.test_symbol, 1250)
        self.assertNotIn(self.test_symbol, self.trading_manager._current_trades)
        self.callback_mock.close_trade.assert_called()
        self.assertNotIn(self.test_symbol, self.trading_manager._current_trades)

    async def test_take_profit_3(self):
        await self.trading_manager._open_trade(TradeDirection.BUY, self.test_symbol, self.test_entry_price)
        trade = self.trading_manager._current_trades[self.test_symbol]

        # Hit TP3
        await self.listener.simulate_price_change(self.test_symbol, 1350)
        self.assertTrue(trade['take_profits_hit'][2])
        self.callback_mock.close_trade.assert_called()
        self.assertNotIn(self.test_symbol, self.trading_manager._current_trades)

    async def test_multiple_trades(self):
        self.test_symbol2 = TradingSymbol.BTCUSD
        entry_price2 = 50000

        await self.trading_manager._open_trade(TradeDirection.BUY, self.test_symbol, self.test_entry_price)
        await self.trading_manager._open_trade(TradeDirection.SELL, self.test_symbol2, entry_price2)

        # Verify both trades are open
        self.assertIn(self.test_symbol, self.trading_manager._current_trades)
        self.assertIn(self.test_symbol2, self.trading_manager._current_trades)

        # Simulate price changes without hitting SL or TP
        await self.listener.simulate_price_change(self.test_symbol, 1301)
        await self.listener.simulate_price_change(self.test_symbol2, 49900)

        # Ensure no trades were closed or modified
        self.callback_mock.close_trade.assert_not_called()
        self.callback_mock.partially_close_trade.assert_not_called()
        self.callback_mock.modify_trade.assert_not_called()
