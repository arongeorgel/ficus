import asyncio

import pandas as pd
from matplotlib import pyplot as plt

from ficus.g.strategies import strategy_exponential_crossover
from ficus.g.test_backtesting import plot_sma, plot_ema
from ficus.mt5.models import TradingSymbol
from ficus.mt5.VantageSim import VantageSim

vantage = VantageSim()
trading_symbols = [TradingSymbol.BTCUSD]


async def async_start_vantage():
    await vantage.connect_account()
    await vantage.prepare_listeners(trading_symbols)
    # await asyncio.sleep(60*60)


def plot_candlesticks(data):
    """
    Plots candlesticks from OHLC data in a pandas DataFrame.

    Args:
        data: A pandas DataFrame with columns 'Datetime', 'Open', 'Close', 'High', 'Low'.
    """
    # Unpack data for easier use
    dates = data['Datetime']
    opens = data['Open']
    closes = data['Close']
    highs = data['High']
    lows = data['Low']

    # Define colors based on closing price relative to opening price
    colors = ['green' if close > open else 'red' for close, open in zip(closes, opens)]

    # Create the candlestick plot
    plt.figure(figsize=(12, 6))
    num_bars = len(dates)
    bar_width = (dates.max() - dates.min()) / (num_bars * 5)  # Adjust multiplier for desired width
    plt.bar(dates, closes - opens, bottom=opens, color=colors, width=bar_width)

    plt.vlines(dates, lows, highs, color=colors, linewidth=1)
    plt.xticks(rotation=45)  # Rotate x-axis labels for readability
    plt.grid(True, linestyle='--', linewidth=0.5)

    plt.xlabel('Date')
    plt.ylabel('Price')

    plt.title('Candlestick Chart')
    plt.tight_layout()


async def async_start_trading():
    symbol = TradingSymbol.BTCUSD
    forex_data = vantage.get_ohlcv_for_symbol(symbol)
    # pd.options.display.max_rows = None
    # print(forex_data)
    plot_candlesticks(forex_data)
    # apply strategy
    windows = 20, 50
    strategy_three = strategy_exponential_crossover(forex_data, windows)
    print(strategy_three.iloc[-1])
    pos = strategy_three.iloc[-1]['Position']
    print(f'p = {pos}')
    plot_ema(plt, strategy_three, windows)

    # Formatting
    plt.legend()
    plt.show()


def start_vantage():
    asyncio.run(async_start_vantage())


def start_trading():
    asyncio.run(async_start_trading())


async def main():
    # Create tasks for both coroutines
    vantage_task = asyncio.create_task(async_start_vantage())
    trading_task = asyncio.create_task(async_start_trading())

    # Wait for both tasks to complete
    await asyncio.gather(vantage_task, trading_task)

    # Keep the main coroutine running
    while True:
        await asyncio.sleep(1)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt as e:
        print(f"An error occurred: {e}")
    finally:
        plt.close()
        print("Performing clean-up actions before exiting.")
