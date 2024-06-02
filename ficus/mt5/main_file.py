import asyncio

from ficus.mt5.TradingSymbols import TradingSymbols
from ficus.mt5.Vantage import Vantage

vantage = Vantage()
trading_symbols = [TradingSymbols.BTCUSD]


async def async_start_vantage():
    await vantage.connect_account()
    await vantage.prepare_listeners(trading_symbols)
    await asyncio.sleep(60*60)


async def async_start_trading():
    while True:
        await asyncio.sleep(60)
        forex_data = vantage.get_ohlcv_for_symbol(TradingSymbols.BTCUSD)
        # fill in the position
        # apply strategy
        # open trades
        print(forex_data)


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
