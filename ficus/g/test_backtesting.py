import asyncio
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf
from colorama import init
from matplotlib import pyplot as plt

from ficus.g.strategies import strategy_simple_crossover, strategy_exponential_crossover, strategy_macd, calculate_ema
from ficus.mt5.TradingManager import TradingManager
from ficus.mt5.listeners.ITradingCallback import ITradingCallback
from ficus.mt5.models import FicusTrade, TradingSymbol, TradeDirection

# Initialize colorama
init()


class BacktestCallback(ITradingCallback):
    capital = 4000.0
    current_high = 0
    current_low = 0

    current_running_price = 0.0

    def update_capital(self, trade: FicusTrade):
        volume_to_close = trade['volume']
        if trade['position'] is TradeDirection.SELL:
            # 2332 - 2330
            price_difference = trade['entry_price'] - self.current_running_price
        else:
            # 2332 + 2334
            price_difference = self.current_running_price - trade['entry_price']

        contract_size = 100
        self.capital = round(self.capital + (volume_to_close * contract_size * price_difference), 2)
        print(f"Updated capital = {self.capital}, current price = {self.current_running_price}")

    async def close_trade(self, trade: FicusTrade, trading_symbol: TradingSymbol):
        self.update_capital(trade)

    async def open_trade(self, symbol: TradingSymbol, direction: TradeDirection, volume: float, stop_loss: float):
        return {'positionId': '12345'}

    async def partially_close_trade(self, trade: FicusTrade, symbol: TradingSymbol):
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


def calculate_dollars(pips, lots):
    return pips * 100 * lots


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


def plot_sma(plt, data, windows):
    plt.subplot(2, 2, 1)
    plt.plot(data['Datetime'], data['Close'], label='Close Price', alpha=0.5)
    plt.plot(data['Datetime'], data['Long_Window'], label=f'SMA {windows[0]}', alpha=0.5)
    plt.plot(data['Datetime'], data['Short_Window'], label=f'SMA {windows[1]}', alpha=0.5)
    # Plot markers for position open (buy)
    buy_signals = data[data['Position'] == 1]
    plt.scatter(buy_signals['Datetime'], buy_signals['Close'], marker='^', color='g', label='Buy Signal')

    # Plot markers for position close (sell)
    sell_signals = data[data['Position'] == -1]
    plt.scatter(sell_signals['Datetime'], sell_signals['Close'], marker='v', color='r', label='Sell Signal')

    plt.title('SMA Buy/Sell')
    plt.legend(loc='upper left')


def plot_ema(plt, data, windows):
    plt.subplot(2, 2, 2)
    plt.plot(data['Datetime'], data['Close'], label='Close Price', alpha=0.5)
    plt.plot(data['Datetime'], data['Long_Window'], label=f'EMA {windows[0]}', alpha=0.5)
    plt.plot(data['Datetime'], data['Short_Window'], label=f'EMA {windows[1]}', alpha=0.5)
    # Plot markers for position open (buy)
    buy_signals = data[data['Position'] == 1]
    plt.scatter(buy_signals['Datetime'], buy_signals['Close'], marker='^', color='g', label='Buy Signal')

    # Plot markers for position close (sell)
    sell_signals = data[data['Position'] == -1]
    plt.scatter(sell_signals['Datetime'], sell_signals['Close'], marker='v', color='r', label='Sell Signal')
    plt.title('EMA Buy/Sell')
    plt.legend(loc='upper left')


def plot_macd(df, ema_window):
    # Price and EMA
    plt.subplot(2, 2, 3)
    plt.plot(df['Datetime'], df['Close'], label='Close Price', alpha=0.5)
    plt.plot(df['Datetime'], df[f'ema_{ema_window}'], label=f'EMA {ema_window}', alpha=0.5)
    plt.scatter(df[df['Position'] == 1]['Datetime'], df[df['Position'] == 1]['Close'], marker='^', color='green', label='Buy Signal', alpha=1)
    plt.scatter(df[df['Position'] == -1]['Datetime'], df[df['Position'] == -1]['Close'], marker='v', color='red', label='Sell Signal', alpha=1)

    plt.title('MACD Strategy')
    plt.legend()


async def main():
    # ticker = 'USDEUR=X'
    ticker = 'GC=F'
    # ticker = 'BTC=F'

    plt.figure(figsize=(14, 7))

    # Download data
    forex_data = download_forex_data(ticker, '2024-06-03', '2024-06-08', '1m')
    windows = (20, 50)

    # Apply SMA strategy
    c1 = BacktestCallback()
    tm1 = TradingManager(c1)
    s1 = strategy_simple_crossover(forex_data, windows)
    await backtest_strategy(tm1, s1, TradingSymbol.XAUUSD)
    print(f'===> {c1.capital}')

    # Apply EMA strategy
    c2 = BacktestCallback()
    tm2 = TradingManager(c2)
    s2 = strategy_exponential_crossover(forex_data, windows)
    await backtest_strategy(tm2, s2, TradingSymbol.XAUUSD)
    print(f'===> {c2.capital}')

    # Apply MACD
    ema_window = 30
    c3 = BacktestCallback()
    tm3 = TradingManager(c3)
    s3 = calculate_ema(forex_data, ema_window)
    s3 = strategy_macd(s3, ema_window)
    await backtest_strategy(tm3, s3, TradingSymbol.XAUUSD)
    print(f'===> {c3.capital}')

    #plts
    plot_sma(plt, s1, windows)
    plot_ema(plt, s2, windows)
    plot_macd(s3, ema_window)

    # Formatting
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    asyncio.run(main())
