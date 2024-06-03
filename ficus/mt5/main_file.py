import asyncio

import pandas as pd

from ficus.g.strategies import exponential_crossover_strategy
from ficus.mt5.TradingSymbols import TradingSymbols
from ficus.mt5.Vantage import Vantage

vantage = Vantage()
trading_symbols = [TradingSymbols.BTCUSD]


async def async_start_vantage():
    await vantage.connect_account()
    await vantage.prepare_listeners(trading_symbols)
    await asyncio.sleep(60*60)


async def async_start_trading():
    current_position = 0
    while True:
        await asyncio.sleep(60)
        symbol = TradingSymbols.BTCUSD
        forex_data = vantage.get_ohlcv_for_symbol(symbol)
        # apply strategy
        strategy_three = exponential_crossover_strategy(forex_data, 5, 10)
        last = strategy_three.tail(1)
        print(last)
        for _, row in last.iterrows():
            signal = row['Position']
            if pd.isna(signal):
                print("signal is nothing")
            else:
                if current_position != 0 and signal != 0 and signal != current_position:
                    print("Closing current order because we received a new signal")
                    current_position = 0
                    await vantage.close_position()

                if current_position == 0 and signal != 0:
                    print(f"Open a new order")
                    current_position = signal
                    await vantage.open_trade(current_position, symbol.name, row['Close'])


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
