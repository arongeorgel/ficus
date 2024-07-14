import asyncio
import logging
from typing import Any

import MetaTrader5 as mt5

open_trades: list[Any] = list()


def ini_metatrader_terminal():
    # Initialize MetaTrader5
    if not mt5.initialize():
        print("Failed to initialize MetaTrader5")
        mt5.shutdown()


def start_monitoring_trades():
    while True:
        # get all positions open
        open_positions = mt5.positions_get()

        # quick check against what is in memory
        if len(open_positions) != len(open_trades):
            logging.error("There is a discrepancy between memory and terminal in trades.")

        # check for prices
        for position in open_positions:
            tick = mt5.symbol_info_tick(position['symbol'])
            memory_trade = next(trade for trade in open_trades if position.ticket == trade.id)

        # check again after 5 seconds
        asyncio.sleep(5)
