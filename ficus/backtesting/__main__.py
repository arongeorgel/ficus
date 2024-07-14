import asyncio
import logging
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf
from colorama import init
from matplotlib import pyplot as plt

from ficus.backtesting.strategies import *
from ficus.metaapi.MetatraderStorage import MetatraderSymbolPriceManager
from ficus.metaapi.TradingManager import TradingManager
from ficus.metaapi.listeners.ITradingCallback import ITradingCallback
from ficus.models.models import FicusTrade, TradingSymbol, TradeDirection
from ficus.ui.ploters import plot_macd, calculate_optimal_grid_size

# Initialize colorama
init()

logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Define the log message format
    filename='app.log',  # Set the log file name
    filemode='w'  # Set the file mode (w for overwrite, a for append)
)
logger = logging.getLogger('ficus_logger')


class BacktestCallback(ITradingCallback):
    capital = 4000.0
    current_high = 0
    current_low = 0
    contract_size = 0

    current_running_price = 0.0

    def __init__(self):
        self.losses = 0
        self.gains = 0

    def update_capital(self, trade: FicusTrade):
        volume_to_close = trade['volume']
        if trade['trade_direction'] == TradeDirection.SELL:
            # 2332 - 2330
            price_difference = trade['entry_price'] - self.current_running_price
        else:
            # 2332 + 2334
            price_difference = self.current_running_price - trade['entry_price']

        money = volume_to_close * self.contract_size * price_difference
        self.capital = round(self.capital + money, 2)
        if money > 0:
            self.gains = self.gains + 1
        else:
            self.losses = self.losses + 1
        logger.info(f"Updated capital = {self.capital}, current price = {self.current_running_price}")

    async def close_trade(self, trade: FicusTrade, trading_symbol: str):
        self.update_capital(trade)

    async def open_trade(self, symbol: str, direction: int, volume: float, stop_loss: float):
        return {'positionId': '12345'}

    async def partially_close_trade(self, trade: FicusTrade, symbol: str):
        self.update_capital(trade)

    async def modify_trade(self, trade: FicusTrade):
        pass


# Function to download Forex data
def download_forex_data(ticker, start_date_str, end_date_str, interval):
    if interval == '0m':
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        data = pd.DataFrame(columns=['Datetime', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'])

        current_date = start_date
        while current_date < end_date:
            next_date = min(current_date + timedelta(days=7), end_date)
            df = yf.download(ticker, start=current_date, end=next_date, interval='1m')
            data = pd.concat([data, df])
            current_date = next_date
        return data
    else:
        data = yf.download(ticker, start=start_date_str, end=end_date_str, interval=interval)

    data.reset_index(inplace=True)
    return data


async def backtest_strategy(trade_manager, data, symbol):
    for index, row in data.iterrows():
        await trade_manager.on_ohclv(row, symbol)
        trade_manager.callback.current_high = row['High']
        trade_manager.callback.current_low = row['Low']
        trade_manager.callback.current_running_price = row['Close']

        if symbol in trade_manager._current_trades:
            trade = trade_manager._current_trades[symbol]
            if trade['trade_direction'] == TradeDirection.BUY:
                await trade_manager.validate_price(row['High'], symbol)
            elif trade['trade_direction'] == TradeDirection.SELL:
                await trade_manager.validate_price(row['Low'], symbol)


async def backtest(chart, ema_window, contract_size, forex_data, symbol, plt_index):
    # Apply MACD
    c3 = BacktestCallback()
    c3.contract_size = contract_size
    tm3 = TradingManager(c3)
    short_window = 10
    long_window = 26
    # s3 = strategy_macd2(forex_data, short_window, long_window)
    # s3 = strategy_macd(forex_data, ema_window, 12)
    s3 = strategy_macd4(forex_data, short_window, long_window)
    await backtest_strategy(tm3, s3, symbol)

    # plt
    s3[f'ema_{short_window}'] = s3['Close'].ewm(span=short_window, adjust=False).mean()
    s3[f'ema_{long_window}'] = s3['Close'].ewm(span=long_window, adjust=False).mean()
    s3['MACD'] = s3[f'ema_{short_window}'] - s3[f'ema_{long_window}']
    s3['Signal_Line'] = s3['MACD'].ewm(span=19, adjust=False).mean()

    plot_macd(symbol, chart, s3, short_window, long_window)
    # plot_candlesticks(chart, s3, plt_index)
    print(f'===> On {symbol} after backtesting now have {c3.capital}. Ration W/L: [{c3.gains}/{c3.losses}]')


async def main():
    symbols_to_backtest = [
        # {'s': TradingSymbol.AUDUSD, 'w': 50, 'c': 100000, 'i': 5},
        # {'s': TradingSymbol.BTCUSD, 'w': 50, 'c': 1, 'i': 5},
        # {'s': TradingSymbol.EURUSD, 'w': 50, 'c': 100000, 'i': 5},
        # {'s': TradingSymbol.GBPUSD, 'w': 50, 'c': 100000, 'i': 5},
        # {'s': TradingSymbol.NZDUSD, 'w': 50, 'c': 100000, 'i': 5},
        # {'s': TradingSymbol.USDCAD, 'w': 50, 'c': 100000, 'i': 5},
        # {'s': TradingSymbol.USDCHF, 'w': 50, 'c': 100000, 'i': 5},
        # {'s': TradingSymbol.USDJPY, 'w': 50, 'c': 1000, 'i': 5},
        {'s': TradingSymbol.XAUUSD, 'w': 30, 'c': 100, 'i': 1}
    ]

    plt.figure(figsize=(14, 7))
    calculate_optimal_grid_size(len(symbols_to_backtest))

    for index, symbol in enumerate(symbols_to_backtest):
        storage = MetatraderSymbolPriceManager(symbol['s'])
        forex_data = storage.generate_ohlcv(interval=symbol['i']).dropna()
        forex_data.to_json('ohlcv_data.json', orient='records', date_format='iso')
        await backtest(plt,
                       symbol['w'],
                       symbol['c'],
                       forex_data,
                       symbol['s'],
                       index + 1)

    # Download data
    # forex_data = download_forex_data(ticker, '2024-06-10', '2024-06-14', f'{interval}m')
    # use local json file

    # Formatting
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.grid()
    plt.show()


if __name__ == '__main__':
    asyncio.run(main())
