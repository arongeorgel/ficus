import asyncio
import unittest

from metaapi_cloud_sdk.metaapi.models import MetatraderTradeResponse

from ficus.mt5.TradingManager import TradingManager
from ficus.mt5.listeners.ITradingCallback import ITradingCallback
from ficus.mt5.models import TradingSymbol, TradeDirection, FicusTrade


class ITradingCallbackMock(ITradingCallback):
    async def open_trade(self, symbol: TradingSymbol, direction: TradeDirection, volume: float):
        # Simulate the behavior of opening a trade and return a mock MetatraderTradeResponse
        return MetatraderTradeResponse(
            numericCode=0,
            stringCode="ERR_NO_ERROR",
            message="Trade opened successfully",
            orderId="123456",
            positionId="789012"
        )

    async def close_trade(self, trade: FicusTrade, symbol: TradingSymbol):
        # Simulate the behavior of closing a trade and return a mock MetatraderTradeResponse
        return MetatraderTradeResponse(
            numericCode=0,
            stringCode="ERR_NO_ERROR",
            message="Trade closed successfully",
            orderId="654321",
            positionId="210987"
        )


class MockSynchronizationListener:
    def __init__(self, manager):
        self.manager = manager

    async def simulate_price_change(self, trading_symbol, price):
        await self.manager.validate_price(price, trading_symbol)


class TestTradingManager(unittest.TestCase):

    def setUp(self):
        self.callback = ITradingCallbackMock()
        self.trading_manager = TradingManager(self.callback)
        self.sync_listener = MockSynchronizationListener(self.trading_manager)

    def test_add_closed_trade(self):
        trade = FicusTrade(
            stop_loss_price=1.2,
            entry_price=1.3,
            position=TradeDirection.BUY,
            take_profit=1.4,
            position_id="123456",
            symbol=TradingSymbol.XAUUSD
        )
        self.trading_manager._add_closed_trade(trade)
        self.assertIn(trade, self.trading_manager._TradingManager__closed_trades)

    def test_close_trade(self):
        trading_symbol = TradingSymbol.XAUUSD
        trade = FicusTrade(
            stop_loss_price=1.2,
            entry_price=1.3,
            position=TradeDirection.BUY,
            take_profit=1.4,
            position_id="123456",
            symbol=trading_symbol
        )
        self.trading_manager._TradingManager__current_trades[trading_symbol] = trade
        self.trading_manager._close_trade(trade, trading_symbol)
        self.assertNotIn(trading_symbol, self.trading_manager._TradingManager__current_trades)

    def test_stop_loss_hit_buy(self):
        trading_symbol = TradingSymbol.XAUUSD
        trade = FicusTrade(
            stop_loss_price=1.0,
            entry_price=1.3,
            position=TradeDirection.BUY,
            take_profit=1.6,
            position_id="123456",
            symbol=trading_symbol
        )
        self.trading_manager._TradingManager__current_trades[trading_symbol] = trade
        asyncio.run(self.sync_listener.simulate_price_change(trading_symbol, 0.9))
        self.assertNotIn(trading_symbol, self.trading_manager._TradingManager__current_trades)

    def test_take_profit_hit_buy(self):
        trading_symbol = TradingSymbol.XAUUSD
        trade = FicusTrade(
            stop_loss_price=1.0,
            entry_price=1.3,
            position=TradeDirection.BUY,
            take_profit=1.6,
            position_id="123456",
            symbol=trading_symbol
        )
        self.trading_manager._TradingManager__current_trades[trading_symbol] = trade
        asyncio.run(self.sync_listener.simulate_price_change(trading_symbol, 1.7))
        self.assertNotIn(trading_symbol, self.trading_manager._TradingManager__current_trades)

    def test_stop_loss_hit_sell(self):
        trading_symbol = TradingSymbol.XAUUSD
        trade = FicusTrade(
            stop_loss_price=1.6,
            entry_price=1.3,
            position=TradeDirection.SELL,
            take_profit=1.0,
            position_id="123456",
            symbol=trading_symbol
        )
        self.trading_manager._TradingManager__current_trades[trading_symbol] = trade
        asyncio.run(self.sync_listener.simulate_price_change(trading_symbol, 1.7))
        self.assertNotIn(trading_symbol, self.trading_manager._TradingManager__current_trades)

    def test_take_profit_hit_sell(self):
        trading_symbol = TradingSymbol.XAUUSD
        trade = FicusTrade(
            stop_loss_price=1.6,
            entry_price=1.3,
            position=TradeDirection.SELL,
            take_profit=1.0,
            position_id="123456",
            symbol=trading_symbol
        )
        self.trading_manager._TradingManager__current_trades[trading_symbol] = trade
        asyncio.run(self.sync_listener.simulate_price_change(trading_symbol, 0.9))
        self.assertNotIn(trading_symbol, self.trading_manager._TradingManager__current_trades)

    def test_price_in_between_no_action(self):
        trading_symbol = TradingSymbol.XAUUSD
        trade = FicusTrade(
            stop_loss_price=1.0,
            entry_price=1.3,
            position=TradeDirection.BUY,
            take_profit=1.6,
            position_id="123456",
            symbol=trading_symbol
        )
        self.trading_manager._TradingManager__current_trades[trading_symbol] = trade
        asyncio.run(self.sync_listener.simulate_price_change(trading_symbol, 1.4))
        self.assertIn(trading_symbol, self.trading_manager._TradingManager__current_trades)

    def test_validate_price(self):
        # You need to mock callback and define its methods to properly test this function
        pass

    def test_open_trade(self):
        direction = TradeDirection.BUY
        trading_symbol = TradingSymbol.XAUUSD
        entry_price = 1.2345
        asyncio.run(self.trading_manager.open_trade(direction, trading_symbol, entry_price))
        self.assertIn(trading_symbol, self.trading_manager._TradingManager__current_trades)

    def test_on_ohclv(self):
        # You need to mock callback and define its methods to properly test this function
        pass

    def test_open_trade_sell(self):
        direction = TradeDirection.SELL
        trading_symbol = TradingSymbol.XAUUSD
        entry_price = 1.2345
        asyncio.run(self.trading_manager.open_trade(direction, trading_symbol, entry_price))
        self.assertIn(trading_symbol, self.trading_manager._TradingManager__current_trades)

    def test_add_multiple_closed_trades(self):
        trade1 = FicusTrade(
            stop_loss_price=1.2,
            entry_price=1.3,
            position=TradeDirection.BUY,
            take_profit=1.4,
            position_id="123456",
            symbol=TradingSymbol.XAUUSD
        )
        trade2 = FicusTrade(
            stop_loss_price=1.5,
            entry_price=1.6,
            position=TradeDirection.SELL,
            take_profit=1.7,
            position_id="789012",
            symbol=TradingSymbol.EURUSD
        )
        self.trading_manager._add_closed_trade(trade1)
        self.trading_manager._add_closed_trade(trade2)
        self.assertIn(trade1, self.trading_manager._TradingManager__closed_trades)
        self.assertIn(trade2, self.trading_manager._TradingManager__closed_trades)

    def test_close_nonexistent_trade(self):
        trading_symbol = TradingSymbol.XAUUSD
        trade = FicusTrade(
            stop_loss_price=1.2,
            entry_price=1.3,
            position=TradeDirection.BUY,
            take_profit=1.4,
            position_id="123456",
            symbol=trading_symbol
        )
        # Trade doesn't exist in current trades, so attempting to close it should not raise an error
        with self.assertRaises(KeyError):
            self.trading_manager._close_trade(trade, trading_symbol)


if __name__ == '__main__':
    unittest.main()
