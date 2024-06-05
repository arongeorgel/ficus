from typing import List

import pandas as pd
from pandas import Series

from ficus.mt5.listeners.ITradingCallback import ITradingCallback
from ficus.mt5.models import TradingSymbol, TradeDirection, FicusTrade


class TradingManager:
    __current_trades: dict[TradingSymbol, FicusTrade]
    __closed_trades: List[FicusTrade] = []

    def __init__(self, callback: ITradingCallback):
        self.__current_trades = {}
        self.callback: ITradingCallback = callback

    def _add_closed_trade(self, order: FicusTrade):
        self.__closed_trades.append(order)

    def _close_trade(self, trade, trading_symbol):
        self._add_closed_trade(trade)
        del self.__current_trades[trading_symbol]

    async def validate_price(self, price: float, trading_symbol):
        if trading_symbol not in TradingSymbol:
            return
        if trading_symbol not in self.__current_trades:
            return

        trade = self.__current_trades[trading_symbol]
        if trade['position'] is TradeDirection.BUY:
            if trade['stop_loss_price'] >= price:
                print(f"Stop loss hit for {trade['symbol']} on buy at price {price}")
                self._close_trade(trade, trading_symbol)
                await self.callback.close_trade(trade, trading_symbol)
            elif trade['take_profit'] <= price:
                print(f"Take profit hit for {trade['symbol']} on buy at price {price}")
                self._close_trade(trade, trading_symbol)
                await self.callback.close_trade(trade, trading_symbol)

        elif trade['position'] is TradeDirection.SELL:
            if trade['stop_loss_price'] <= price:
                print(f"Stop loss hit for {trade['symbol']} on sell at price {price}")
                self._close_trade(trade, trading_symbol)
                await self.callback.close_trade(trade, trading_symbol)
            elif trade['take_profit'] >= price:
                print(f"Take profit hit for {trade['symbol']} on sell at price {price}")
                self._close_trade(trade, trading_symbol)
                await self.callback.close_trade(trade, trading_symbol)

    async def open_trade(self, direction: TradeDirection, trading_symbol: TradingSymbol, entry_price: float):
        result = await self.callback.open_trade(symbol=trading_symbol, volume=0.02, direction=direction)
        trade = FicusTrade(
            entry_price=entry_price,
            stop_loss_price=TradingSymbol.calculate_stop_loss_price(trading_symbol, entry_price, direction),
            position=direction,
            take_profit=TradingSymbol.calculate_take_profit(trading_symbol, entry_price, direction),
            position_id=result['positionId'],
            symbol=trading_symbol)
        self.__current_trades[trading_symbol] = trade
        print(f"Open a new trade ${trade}")

    async def on_ohclv(self, series: Series, symbol: TradingSymbol):
        signal = series['Position']
        if pd.isna(signal):
            print("No signal")
            return

        # if we have a running trade, but received a different direction, close it.
        if symbol in self.__current_trades:
            trade = self.__current_trades[symbol]
            if signal != 0 and signal != trade['position']:
                print(f"New signal received ({signal}). Closing {trade} at price {series['Close']}")
                self._close_trade(trade, symbol)
                await self.callback.close_trade(trade, symbol)
        elif signal != 0:
            await self.open_trade(TradeDirection.from_value(signal), symbol, series['Close'])

