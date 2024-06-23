import json
import logging
import traceback
from typing import List

import pandas as pd
from pandas import Series

from ficus.mt5.listeners.ITradingCallback import ITradingCallback
from ficus.mt5.models import TradeDirection, FicusTrade, TradingSymbol

logger = logging.getLogger('ficus_logger')


class TradingManager:
    _current_trades: dict[str, FicusTrade]
    _closed_trades: List[FicusTrade] = []

    def __init__(self, callback: ITradingCallback):
        self._current_trades = {}
        self.callback: ITradingCallback = callback
        self.load_open_trades_file()

    def load_open_trades_file(self):
        try:
            with open('open_trades.json', 'r') as file:
                self._current_trades = json.load(file)
        except FileNotFoundError:
            pass  # If the file is not found, just pass

    async def save_open_trades_to_file(self):
        try:
            with open('open_trades.json', 'w') as file:
                json.dump(self._current_trades, file, indent=4)
        except Exception:
            logger.error(f"Failed to save open trades {traceback.format_exc()}")

    async def on_closed_by_broker(self, position_id):
        logger.info(f"Closing trade because it was removed by broker. Trade: {position_id}")
        for key, trade in self._current_trades.copy().items():
            if trade['position_id'] == position_id:
                trade['close_reason'] = "Removed by broker"
                self._closed_trades.append(trade)
                del self._current_trades[trade['symbol']]
                await self.save_open_trades_to_file()
                with open('closed_trades.json', 'w') as file:
                    json.dump(self._closed_trades, file, indent=4)

    async def _close_trade(self, trade, trading_symbol, close_reason):
        logger.info(f"Closing trade because {close_reason}. Trade: {trade}")
        trade['close_reason'] = close_reason
        self._closed_trades.append(trade)
        del self._current_trades[trading_symbol]
        await self.save_open_trades_to_file()
        await self.callback.close_trade(trade, trading_symbol)

        with open('closed_trades.json', 'w') as file:
            json.dump(self._closed_trades, file, indent=4)

    async def _partially_close_trade(self, trade, trading_symbol):
        await self.callback.partially_close_trade(trade, trading_symbol)
        await self.save_open_trades_to_file()

    async def _modify_trade(self, trade: FicusTrade):
        self._current_trades[trade['symbol']] = trade
        await self.callback.modify_trade(trade)
        await self.save_open_trades_to_file()

    async def _open_trade(self, direction: int, trading_symbol: str, entry_price: float):
        sl, tp1, tp2, tp3, volume = TradingSymbol.calculate_levels(trading_symbol, entry_price, direction)

        result = await self.callback.open_trade(symbol=trading_symbol, volume=volume, direction=direction, stop_loss=sl)
        trade = FicusTrade(
            entry_price=entry_price,
            stop_loss_price=sl,
            take_profits=(tp1, tp2, tp3),
            trade_direction=direction,
            position_id=result['positionId'],
            take_profits_hit=[False, False, False],
            start_volume=volume,
            volume=volume,
            symbol=trading_symbol)
        self._current_trades[trading_symbol] = trade

        await self.save_open_trades_to_file()

        logger.info(f"Open a new trade ${trade}")

    async def validate_price(self, price: float, trading_symbol):
        if trading_symbol not in self._current_trades:
            return

        trade = self._current_trades[trading_symbol]
        direction = trade['trade_direction']
        entry_price = trade['entry_price']
        volume = trade['start_volume']

        if direction == TradeDirection.BUY:
            # SL
            if price <= trade['stop_loss_price']:
                logger.info(f"Stop loss hit for {trade['symbol']} on buy at price {price}")
                await self._close_trade(trade, trading_symbol, "stop loss hit on buy")
            # TP3
            elif price >= trade['take_profits'][2] and not trade['take_profits_hit'][2]:
                logger.info(f"Take profit 3 hit for {trade['symbol']} on buy at price {price}")
                trade['take_profits_hit'][2] = True
                await self._close_trade(trade, trading_symbol, "all TP hit on buy")
            # TP2
            elif price >= trade['take_profits'][1] and not trade['take_profits_hit'][1]:
                logger.info(f"Take profit 2 hit for {trade['symbol']} on buy at price {price}")
                trade['volume'] = round(volume / 3, 2)
                await self._partially_close_trade(trade, trading_symbol)

                # modify the position
                trade['stop_loss_price'] = entry_price
                trade['take_profits_hit'][1] = True
                await self._modify_trade(trade)
            # TP 1
            elif price >= trade['take_profits'][0] and not trade['take_profits_hit'][0]:
                logger.info(f"Take profit 1 hit for {trade['symbol']} on buy at price {price}")
                trade['take_profits_hit'][0] = True
                trade['volume'] = round(volume / 2, 2)
                await self._partially_close_trade(trade, trading_symbol)

                # modify the position, update stop loss
                trade['stop_loss_price'] = entry_price - ((entry_price - trade['stop_loss_price']) / 2)
                await self._modify_trade(trade)

        elif direction == TradeDirection.SELL:
            # SL
            if price >= trade['stop_loss_price']:
                logger.info(f"Stop loss hit for {trade['symbol']} on sell at price {price}")
                await self._close_trade(trade, trading_symbol, "stop loss hit on sell")
            # TP 3
            elif price <= trade['take_profits'][2] and not trade['take_profits_hit'][2]:
                logger.info(f"Take profit 3 hit for {trade['symbol']} on sell at price {price}")
                trade['take_profits_hit'][2] = True
                await self._close_trade(trade, trading_symbol, "all TP hit on sell")
            # TP 2
            elif price <= trade['take_profits'][1] and not trade['take_profits_hit'][1]:
                logger.info(f"Take profit 2 hit for {trade['symbol']} on sell at price {price}")
                trade['volume'] = round(volume / 3, 2)
                await self._partially_close_trade(trade, trading_symbol)

                # modify the position
                trade['stop_loss_price'] = entry_price
                trade['take_profits_hit'][1] = True
                await self._modify_trade(trade)
            # TP 1
            elif price <= trade['take_profits'][0] and not trade['take_profits_hit'][0]:
                logger.info(f"Take profit 1 hit for {trade['symbol']} on buy at price {price}")
                trade['take_profits_hit'][0] = True
                trade['volume'] = round(volume / 2, 2)
                await self._partially_close_trade(trade, trading_symbol)

                # modify the position, update stop loss
                trade['stop_loss_price'] = entry_price + ((entry_price - trade['stop_loss_price']) / 2)
                await self._modify_trade(trade)

    async def on_ohclv(self, series: Series, symbol: str):
        signal = int(series['Position'])
        if pd.isna(signal):
            return

        # if we have a running trade, but received a different direction, close it.
        if symbol in self._current_trades:
            trade = self._current_trades[symbol]
            if signal != 0 and signal != trade['trade_direction']:
                logger.info(f"New signal received ({signal}). Closing {trade} at price {series['Close']}")
                await self._close_trade(trade, symbol, f"received new signal ({signal})")
                await self._open_trade(signal, symbol, series['Close'])
        else:
            if signal != 0:
                await self._open_trade(signal, symbol, series['Close'])
