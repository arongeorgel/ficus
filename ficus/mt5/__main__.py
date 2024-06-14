import asyncio
import logging
import os

from ficus.backtesting.strategies import calculate_ema, strategy_macd
from ficus.mt5.Vantage import Vantage
from ficus.mt5.models import TradingSymbol

# Imports the Cloud Logging client library
import google.cloud.logging

# Instantiates a client
client = google.cloud.logging.Client()

# Retrieves a Cloud Logging handler based on the environment
# you're running in and integrates the handler with the
# Python logging module. By default this captures all logs
# at INFO level and higher
client.setup_logging()

# Start Ficus
vantage = Vantage()
trading_symbols = [TradingSymbol.XAUUSD, TradingSymbol.BTCUSD]


async def async_start_vantage():
    await vantage.connect_account()
    await vantage.prepare_listeners(trading_symbols)
    # run this for 12 hours
    await asyncio.sleep(60 * 60 * 24)


async def async_start_trading_gold():
    while True:
        try:
            trade_on_minutes = 1
            await asyncio.sleep(60 * trade_on_minutes)
            gold = TradingSymbol.XAUUSD
            gold_ohlcv = vantage.get_ohlcv_for_symbol(gold, trade_on_minutes)
            # apply strategy
            gold_ema = calculate_ema(gold_ohlcv, 50)
            gold_macd = strategy_macd(gold_ema, 50)
            last_gold = gold_macd.iloc[-1]
            await vantage.on_ohlcv(last_gold, gold)
        except Exception as e:
            logging.error(f"Failed for gold. Traceback: {e.__traceback__}")


async def async_start_trading_bitcoin():
    while True:
        try:
            trade_on_minutes = 5
            await asyncio.sleep(60 * trade_on_minutes)
            bitcoin = TradingSymbol.BTCUSD
            btc_ohlcv = vantage.get_ohlcv_for_symbol(bitcoin, trade_on_minutes)
            # apply strategy
            btc_ema = calculate_ema(btc_ohlcv, 50)
            btc_macd = strategy_macd(btc_ema, 50)
            last_btc = btc_macd.iloc[-1]
            await vantage.on_ohlcv(last_btc, bitcoin)
        except Exception as e:
            logging.error(f"Failed for bitcoin. Traceback: {e.__traceback__}")


def start_vantage():
    asyncio.run(async_start_vantage())


async def main():
    try:
        # Create tasks for both coroutines
        vantage_task = asyncio.create_task(async_start_vantage())
        gold_task = asyncio.create_task(async_start_trading_gold())
        btc_task = asyncio.create_task(async_start_trading_bitcoin())

        # Wait for both tasks to complete
        await asyncio.gather(vantage_task, gold_task, btc_task)

        # Keep the main coroutine running
        while True:
            await asyncio.sleep(1)
    except Exception as e:
        logging.error(f"Exception in main(). Traceback: {e.__traceback__}")
    finally:
        logging.info("Program completed. Starting again now")
        logging.info("=====================================")
        os.system("run_ficus")


async def main_disconnect():
    await vantage.disconnect(trading_symbols)


if __name__ == '__main__':
    asyncio.run(main())
