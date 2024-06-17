import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from ficus.mt5.MetatraderStorage import MetatraderSymbolPriceManager
from ficus.mt5.models import TradingSymbol


def macd_signal(data, short_window=12, long_window=26, signal_window=9):
    # Calculate the short and long EMAs
    data['EMA12'] = data['Close'].ewm(span=short_window, adjust=False).mean()
    data['EMA26'] = data['Close'].ewm(span=long_window, adjust=False).mean()

    # Calculate the MACD line
    data['MACD'] = data['EMA12'] - data['EMA26']

    # Calculate the Signal line
    data['Signal'] = data['MACD'].ewm(span=signal_window, adjust=False).mean()

    # ==
    # ema_short = df['Close'].ewm(span=short_window, adjust=False).mean()
    # ema_long = df['Close'].ewm(span=long_window, adjust=False).mean()
    # macd = ema_short - ema_long
    # signal_line = macd.ewm(span=signal_window, adjust=False).mean()
    # ==

    # Generate MACD buy/sell signals
    data['MACD_Signal'] = np.where(data['MACD'] > data['Signal'], 1, 0)
    data['MACD_Signal'] = np.where(data['MACD'] < data['Signal'], -1, data['MACD_Signal'])

    return data

def rsi(data, window=14):
    delta = data['Close'].diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    RS = gain / loss
    data['RSI'] = 100 - (100 / (1 + RS))

    return data

def adx(data, window=14):
    df = data.copy()
    df['TR'] = np.maximum(df['High'], df['Close'].shift(1)) - np.minimum(df['Low'], df['Close'].shift(1))
    df['+DM'] = np.where((df['High'] - df['High'].shift(1)) > (df['Low'].shift(1) - df['Low']), df['High'] - df['High'].shift(1), 0)
    df['-DM'] = np.where((df['Low'].shift(1) - df['Low']) > (df['High'] - df['High'].shift(1)), df['Low'].shift(1) - df['Low'], 0)

    df['+DI'] = 100 * (df['+DM'].ewm(span=window, adjust=False).mean() / df['TR'].ewm(span=window, adjust=False).mean())
    df['-DI'] = 100 * (df['-DM'].ewm(span=window, adjust=False).mean() / df['TR'].ewm(span=window, adjust=False).mean())
    df['DX'] = (np.abs(df['+DI'] - df['-DI']) / np.abs(df['+DI'] + df['-DI'])) * 100
    df['ADX'] = df['DX'].ewm(span=window, adjust=False).mean()

    data['ADX'] = df['ADX']

    return data

def generate_signals(data):
    # Apply MACD
    data = macd_signal(data)

    # Apply RSI
    data = rsi(data)

    # Apply ADX
    data = adx(data)

    # Generate buy/sell signals
    buy_signal = (data['MACD_Signal'] == 1) & (data['RSI'] < 30) & (data['ADX'] > 25)
    sell_signal = (data['MACD_Signal'] == -1) & (data['RSI'] > 70) & (data['ADX'] > 25)

    data['Buy_Signal'] = np.where(buy_signal, 1, 0)
    data['Sell_Signal'] = np.where(sell_signal, 1, 0)

    return data

# Example usage
if __name__ == "__main__":
    # Sample data (you can replace this with actual OHLCV data)
    storage = MetatraderSymbolPriceManager(TradingSymbol.XAUUSD)
    data = storage.generate_ohlcv(1)

    # Generate signals
    data = generate_signals(data)

    # Plot the data with signals
    plt.figure(figsize=(14, 7))
    plt.plot(data['Close'], label='Close Price', color='b')
    plt.plot(data['MACD'], label='MACD')
    plt.plot(data['Signal'], label='Signal Line')
    plt.scatter(data.index, data['Buy_Signal'] * data['Close'], label='Buy Signal', marker='^', color='g')
    plt.scatter(data.index, data['Sell_Signal'] * data['Close'], label='Sell Signal', marker='v', color='r')
    plt.legend()
    plt.show()
