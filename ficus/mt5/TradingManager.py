from typing import List

import pandas as pd
from pandas import Series

from ficus.mt5.listeners.ITradingCallback import ITradingCallback
from ficus.mt5.models import TradingSymbol, TradeDirection, FicusTrade


class TradingManager:
    _current_trades: dict[TradingSymbol, FicusTrade]
    __closed_trades: List[FicusTrade] = []

    def __init__(self, callback: ITradingCallback):
        self._current_trades = {}
        self.callback: ITradingCallback = callback

    async def _close_trade(self, trade, trading_symbol):
        print(f"Closing trade {trade}")
        self.__closed_trades.append(trade)
        del self._current_trades[trading_symbol]
        await self.callback.close_trade(trade, trading_symbol)

    async def _partially_close_trade(self, trade, trading_symbol):
        await self.callback.partially_close_trade(trade, trading_symbol)

    async def _modify_trade(self, trade):
        await self.callback.modify_trade(trade)

    async def _open_trade(self, direction: TradeDirection, trading_symbol: TradingSymbol, entry_price: float):
        sl, tp1, tp2, tp3, volume = trading_symbol.calculate_levels(entry_price, direction)

        result = await self.callback.open_trade(symbol=trading_symbol, volume=volume,direction=direction, stop_loss=sl)
        trade = FicusTrade(
            entry_price=entry_price,
            stop_loss_price=sl,
            take_profits=(tp1, tp2, tp3),
            position=direction,
            position_id=result['positionId'],
            take_profits_hit=[False, False, False],
            start_volume=volume,
            volume=volume,
            symbol=trading_symbol)
        self._current_trades[trading_symbol] = trade
        print(f"Open a new trade ${trade}")

    async def validate_price(self, price: float, trading_symbol):
        if trading_symbol not in TradingSymbol:
            return
        if trading_symbol not in self._current_trades:
            return

        trade = self._current_trades[trading_symbol]
        direction = trade['position']
        entry_price = trade['entry_price']
        volume = trade['start_volume']

        # def adjust_stop_loss(new_sl):
        #     trade['stop_loss_price'] = new_sl
        #     print(f"Stop loss adjusted to {new_sl} for {trade['symbol']}")

        if direction is TradeDirection.BUY:
            # SL
            if price <= trade['stop_loss_price']:
                print(f"Stop loss hit for {trade['symbol']} on buy at price {price}")
                await self._close_trade(trade, trading_symbol)
            # TP3
            elif price >= trade['take_profits'][2] and not trade['take_profits_hit'][2]:
                print(f"Take profit 3 hit for {trade['symbol']} on buy at price {price}")
                trade['take_profits_hit'][2] = True
                await self._close_trade(trade, trading_symbol)
            # TP2
            elif price >= trade['take_profits'][1] and not trade['take_profits_hit'][1]:
                print(f"Take profit 2 hit for {trade['symbol']} on buy at price {price}")
                trade['volume'] = round(volume / 3, 2)
                await self._partially_close_trade(trade, trading_symbol)

                # modify the position
                trade['stop_loss_price'] = entry_price
                trade['take_profits_hit'][1] = True
                await self._modify_trade(trade)
            # TP 1
            elif price >= trade['take_profits'][0] and not trade['take_profits_hit'][0]:
                print(f"Take profit 1 hit for {trade['symbol']} on buy at price {price}")
                trade['take_profits_hit'][0] = True
                trade['volume'] = round(volume / 2, 2)
                await self._partially_close_trade(trade, trading_symbol)

                # modify the position, update stop loss
                trade['stop_loss_price'] = entry_price - ((entry_price - trade['stop_loss_price']) / 2)
                await self._modify_trade(trade)

        elif direction is TradeDirection.SELL:
            # SL
            if price >= trade['stop_loss_price']:
                print(f"Stop loss hit for {trade['symbol']} on sell at price {price}")
                await self._close_trade(trade, trading_symbol)
            # TP 3
            elif price <= trade['take_profits'][2] and not trade['take_profits_hit'][2]:
                print(f"Take profit 3 hit for {trade['symbol']} on sell at price {price}")
                trade['take_profits_hit'][2] = True
                await self._close_trade(trade, trading_symbol)
            # TP 2
            elif price <= trade['take_profits'][1] and not trade['take_profits_hit'][1]:
                print(f"Take profit 2 hit for {trade['symbol']} on sell at price {price}")
                trade['volume'] = round(volume / 3, 2)
                await self._partially_close_trade(trade, trading_symbol)

                # modify the position
                trade['stop_loss_price'] = entry_price
                trade['take_profits_hit'][1] = True
                await self._modify_trade(trade)
            # TP 1
            elif price <= trade['take_profits'][0] and not trade['take_profits_hit'][0]:
                print(f"Take profit 1 hit for {trade['symbol']} on buy at price {price}")
                trade['take_profits_hit'][0] = True
                trade['volume'] = round(volume / 2, 2)
                await self._partially_close_trade(trade, trading_symbol)

                # modify the position, update stop loss
                trade['stop_loss_price'] = entry_price + ((entry_price - trade['stop_loss_price']) / 2)
                await self._modify_trade(trade)

    async def on_ohclv(self, series: Series, symbol: TradingSymbol):
        signal = series['Position']
        if pd.isna(signal):
            print("No signal")
            return

        # if we have a running trade, but received a different direction, close it.
        if symbol in self._current_trades:
            trade = self._current_trades[symbol]
            if signal != 0 and TradeDirection.from_value(signal) != trade['position']:
                print(f"New signal received ({signal}). Closing {trade} at price {series['Close']}")
                await self._close_trade(trade, symbol)
        else:
            if signal != 0:
                await self._open_trade(TradeDirection.from_value(signal), symbol, series['Close'])
