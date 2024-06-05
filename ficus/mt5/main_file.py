import asyncio

import pandas as pd

from ficus.g.strategies import exponential_crossover_strategy
from ficus.mt5.Vantage import Vantage
from ficus.mt5.models import TradingSymbol

vantage = Vantage()
trading_symbols = [TradingSymbol.XAUUSD, TradingSymbol.BTCUSD]


async def async_start_vantage():
    await vantage.connect_account()
    await vantage.prepare_listeners(trading_symbols)
    # run this for 12 hours
    await asyncio.sleep(60*60*12)


async def async_start_trading():
    while True:
        await asyncio.sleep(60)
        gold = TradingSymbol.XAUUSD
        forex_data = vantage.get_ohlcv_for_symbol(gold)
        # apply strategy
        strategy_three = exponential_crossover_strategy(forex_data, 5, 10)
        last_ohlcv = strategy_three.iloc[-1]
        await vantage.on_ohlcv(last_ohlcv, gold)

        await asyncio.sleep(1)
        bitcoin = TradingSymbol.BTCUSD
        forex_data = vantage.get_ohlcv_for_symbol(bitcoin)
        # apply strategy
        strategy_three = exponential_crossover_strategy(forex_data, 5, 10)
        last_ohlcv = strategy_three.iloc[-1]
        await vantage.on_ohlcv(last_ohlcv, bitcoin)


def start_vantage():
    asyncio.run(async_start_vantage())


def start_trading():
    asyncio.run(async_start_trading())


async def main():
    try:
        # Create tasks for both coroutines
        vantage_task = asyncio.create_task(async_start_vantage())
        trading_task = asyncio.create_task(async_start_trading())

        # Wait for both tasks to complete
        await asyncio.gather(vantage_task, trading_task)

        # Keep the main coroutine running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await vantage.disconnect(trading_symbols)
        print("terminated by key")


if __name__ == '__main__':
    asyncio.run(main())
