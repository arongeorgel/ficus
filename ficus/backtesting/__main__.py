import asyncio
import logging
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf
from colorama import init
from matplotlib import pyplot as plt

from ficus.backtesting.strategies import *
from ficus.mt5.TradingManager import TradingManager
from ficus.mt5.listeners.ITradingCallback import ITradingCallback
from ficus.mt5.models import FicusTrade, TradingSymbol, TradeDirection
from ficus.ui.ploters import plot_sma, plot_ema, plot_macd

# Initialize colorama
init()


class BacktestCallback(ITradingCallback):
    capital = 4000.0
    current_high = 0
    current_low = 0
    contract_size = 0

    current_running_price = 0.0

    def update_capital(self, trade: FicusTrade):
        volume_to_close = trade['volume']
        if trade['position'] is TradeDirection.SELL:
            # 2332 - 2330
            price_difference = trade['entry_price'] - self.current_running_price
        else:
            # 2332 + 2334
            price_difference = self.current_running_price - trade['entry_price']

        self.capital = round(self.capital + (volume_to_close * self.contract_size * price_difference), 2)
        logging.info("Updated capital = {self.capital}, current price = {self.current_running_price}")

    async def close_trade(self, trade: FicusTrade, trading_symbol: str):
        self.update_capital(trade)

    async def open_trade(self, symbol: str, direction: TradeDirection, volume: float, stop_loss: float):
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
            if trade['position'] is TradeDirection.BUY:
                await trade_manager.validate_price(row['High'], symbol)
            elif trade["position"] is TradeDirection.SELL:
                await trade_manager.validate_price(row['Low'], symbol)


async def main():
    # ticker = 'EURUSD=X'
    # symbol = TradingSymbol.EURUSD
    # contract_size = 100000

    ticker = 'GC=F'
    symbol = TradingSymbol.XAUUSD
    contract_size = 100

    # ticker = 'BTC=F'
    # symbol = TradingSymbol.BTCUSD
    # contract_size = 1

    interval = '5m'

    plt.figure(figsize=(14, 7))

    # Download data
    forex_data = download_forex_data(ticker, '2024-06-10', '2024-06-14', interval)
    # use local json file
    # storage = MetatraderSymbolPriceManager(TradingSymbol.XAUUSD)
    # forex_data = storage.generate_ohlcv(1)
    windows = (20, 50)

    # Apply SMA strategy
    c1 = BacktestCallback()
    c1.contract_size = contract_size
    tm1 = TradingManager(c1)
    s1 = strategy_simple_crossover(forex_data, windows)
    await backtest_strategy(tm1, s1, symbol)
    print(f'===> {c1.capital}')

    # Apply EMA strategy
    c2 = BacktestCallback()
    c2.contract_size = contract_size
    tm2 = TradingManager(c2)
    s2 = strategy_exponential_crossover(forex_data, windows)
    await backtest_strategy(tm2, s2, symbol)
    print(f'===> {c2.capital}')

    # Apply MACD
    ema_window = 30
    c3 = BacktestCallback()
    c3.contract_size = contract_size
    tm3 = TradingManager(c3)
    s3 = calculate_ema(forex_data, ema_window)
    s3 = strategy_macd(s3, ema_window)
    await backtest_strategy(tm3, s3, symbol)
    print(f'===> {c3.capital}')

    # plts
    plot_sma(plt, s1, windows)
    plot_ema(plt, s2, windows)
    plot_macd(plt, s3, ema_window)

    # Formatting
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    asyncio.run(main())
