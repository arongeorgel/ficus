import asyncio

import pandas as pd

from ficus.g.strategies import strategy_exponential_crossover, strategy_macd, calculate_ema
from ficus.mt5.Vantage import Vantage
from ficus.mt5.models import TradingSymbol

vantage = Vantage()
trading_symbols = [TradingSymbol.BTCUSD, TradingSymbol.XAUUSD]


async def async_start_vantage():
    await vantage.connect_account()
    await vantage.prepare_listeners(trading_symbols)
    # run this for 12 hours
    await asyncio.sleep(60*60*12)


async def async_start_trading():
    while True:
        try:
            await asyncio.sleep(60)
            gold = TradingSymbol.XAUUSD
            gold_ohlcv = vantage.get_ohlcv_for_symbol(gold)
            # apply strategy
            gold_ema = calculate_ema(gold_ohlcv, 50)
            gold_macd = strategy_macd(gold_ema, 50)
            last_gold = gold_macd.iloc[-1]
            await vantage.on_ohlcv(last_gold, gold)

            await asyncio.sleep(1)

            bitcoin = TradingSymbol.BTCUSD
            btc_ohlcv = vantage.get_ohlcv_for_symbol(bitcoin)
            # apply strategy
            btc_ema = calculate_ema(btc_ohlcv, 50)
            btc_macd = strategy_macd(btc_ema, 50)
            last_btc = btc_macd.iloc[-1]
            await vantage.on_ohlcv(last_btc, bitcoin)
        except Exception as e:
            print(f"Failed where? {e.with_traceback()}")


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
    except Exception as e:
        print(f"terminated by {e}")
    finally:
        print("finally terminated by key")
        # await vantage.disconnect(trading_symbols)
        print("DONE!")


async def main_disconnect():
    await vantage.disconnect(trading_symbols)


if __name__ == '__main__':
    asyncio.run(main())
