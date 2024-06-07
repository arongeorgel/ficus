import unittest
from abc import ABC
from unittest.mock import AsyncMock

from ficus.mt5.TradingManager import TradingManager
from ficus.mt5.listeners.ITradingCallback import ITradingCallback
from ficus.mt5.models import TradingSymbol, TradeDirection, FicusTrade


class ITradingCallbackMock(ITradingCallback, ABC):
    async def close_trade(self, trade: FicusTrade, symbol: TradingSymbol):
        pass

    async def partially_close_trade(self, trade: FicusTrade, symbol: TradingSymbol):
        pass

    async def modify_trade(self, trade: FicusTrade):
        pass

    async def open_trade(self, symbol: TradingSymbol, direction: TradeDirection, volume: float, stop_loss):
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

    async def test_open_trade_buy(self):
        symbol = TradingSymbol.XAUUSD
        entry_price = 1000
        await self.trading_manager._open_trade(TradeDirection.BUY, symbol, entry_price)

        self.assertIn(symbol, self.trading_manager._current_trades)
        trade = self.trading_manager._current_trades[symbol]
        self.assertEqual(trade['position'], TradeDirection.BUY)

    async def test_open_trade_sell(self):
        symbol = TradingSymbol.XAUUSD
        entry_price = 1000
        await self.trading_manager._open_trade(TradeDirection.SELL, symbol, entry_price)

        self.assertIn(symbol, self.trading_manager._current_trades)
        trade = self.trading_manager._current_trades[symbol]
        self.assertEqual(trade['position'], TradeDirection.SELL)

    async def test_close_trade(self):
        symbol = TradingSymbol.XAUUSD
        entry_price = 1000
        await self.trading_manager._open_trade(TradeDirection.BUY, symbol, entry_price)
        await self.listener.simulate_price_change(symbol, 900)  # Trigger SL

        self.assertNotIn(symbol, self.trading_manager._current_trades)
        self.callback_mock.close_trade.assert_called()

    async def test_take_profit_levels(self):
        symbol = TradingSymbol.XAUUSD
        entry_price = 1000
        await self.trading_manager._open_trade(TradeDirection.BUY, symbol, entry_price)
        trade = self.trading_manager._current_trades[symbol]

        # Hit TP1
        await self.listener.simulate_price_change(symbol, 1004)
        self.assertTrue(trade['take_profits_hit'][0])
        self.callback_mock.modify_trade.assert_called()

        # Hit TP2
        await self.listener.simulate_price_change(symbol, 1005)
        self.assertTrue(trade['take_profits_hit'][1])
        self.callback_mock.partially_close_trade.assert_called()

        # Hit TP3
        await self.listener.simulate_price_change(symbol, 1011)
        self.assertTrue(trade['take_profits_hit'][2])
        self.callback_mock.close_trade.assert_called()

    async def test_price_fluctuation(self):
        symbol = TradingSymbol.XAUUSD
        entry_price = 1000
        await self.trading_manager._open_trade(TradeDirection.BUY, symbol, entry_price)
        self.assertIn(symbol, self.trading_manager._current_trades)
        self.callback_mock.open_trade.assert_called()

        trade = self.trading_manager._current_trades[symbol]

        # Hit TP1
        await self.listener.simulate_price_change(symbol, 1004)
        self.assertTrue(trade['take_profits_hit'][0])
        self.callback_mock.modify_trade.assert_called()

        # Price drops but no SL hit
        await self.listener.simulate_price_change(symbol, 1002.5)
        self.assertTrue(trade['take_profits_hit'][0])

        # Hit TP2
        await self.listener.simulate_price_change(symbol, 1005)
        self.assertTrue(trade['take_profits_hit'][1])
        self.callback_mock.partially_close_trade.assert_called()

    async def test_take_profit_1_and_stop_loss(self):
        symbol = TradingSymbol.XAUUSD
        entry_price = 1000
        await self.trading_manager._open_trade(TradeDirection.BUY, symbol, entry_price)
        trade = self.trading_manager._current_trades[symbol]

        # Hit TP1
        await self.listener.simulate_price_change(symbol, 1003)
        self.assertTrue(trade['take_profits_hit'][0])
        self.callback_mock.modify_trade.assert_called()

        # Hit SL
        await self.listener.simulate_price_change(symbol, 950)
        self.assertNotIn(symbol, self.trading_manager._current_trades)
        self.callback_mock.close_trade.assert_called()

    async def test_take_profit_2_and_stop_loss(self):
        symbol = TradingSymbol.XAUUSD
        entry_price = 1000
        await self.trading_manager._open_trade(TradeDirection.BUY, symbol, entry_price)
        trade = self.trading_manager._current_trades[symbol]

        # Hit TP2
        await self.listener.simulate_price_change(symbol, 1005)
        self.assertTrue(trade['take_profits_hit'][1])
        self.callback_mock.partially_close_trade.assert_called()

        # Hit SL
        await self.listener.simulate_price_change(symbol, 900)
        self.assertNotIn(symbol, self.trading_manager._current_trades)
        self.callback_mock.close_trade.assert_called()

    async def test_take_profit_3(self):
        symbol = TradingSymbol.XAUUSD
        entry_price = 1000
        await self.trading_manager._open_trade(TradeDirection.BUY, symbol, entry_price)
        trade = self.trading_manager._current_trades[symbol]

        # Hit TP3
        await self.listener.simulate_price_change(symbol, 1150)
        self.assertTrue(trade['take_profits_hit'][2])
        self.callback_mock.close_trade.assert_called()

    async def test_multiple_trades(self):
        symbol1 = TradingSymbol.XAUUSD
        symbol2 = TradingSymbol.BTCUSD
        entry_price1 = 1000
        entry_price2 = 50000

        await self.trading_manager._open_trade(TradeDirection.BUY, symbol1, entry_price1)
        await self.trading_manager._open_trade(TradeDirection.SELL, symbol2, entry_price2)

        # Verify both trades are open
        self.assertIn(symbol1, self.trading_manager._current_trades)
        self.assertIn(symbol2, self.trading_manager._current_trades)

        # Simulate price changes without hitting SL or TP
        await self.listener.simulate_price_change(symbol1, 1001)
        await self.listener.simulate_price_change(symbol2, 49900)

        # Ensure no trades were closed or modified
        self.callback_mock.close_trade.assert_not_called()
        self.callback_mock.partially_close_trade.assert_not_called()
        self.callback_mock.modify_trade.assert_not_called()
