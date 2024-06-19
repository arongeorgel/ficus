import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from ficus.mt5.MetatraderStorage import MetatraderSymbolPriceManager
from ficus.mt5.models import TradingSymbol


def generate_macd_signals(df, short_window=12, long_window=26, signal_window=9, rsi_window=14, rsi_overbought=70, rsi_oversold=30):
    """
    Generate buy/sell signals based on MACD with trend confirmation using RSI.

    Parameters:
    df (pd.DataFrame): DataFrame with columns ['Open', 'High', 'Low', 'Close', 'Volume']
    short_window (int): Short window period for MACD calculation.
    long_window (int): Long window period for MACD calculation.
    signal_window (int): Signal window period for MACD calculation.
    rsi_window (int): Window period for RSI calculation.
    rsi_overbought (int): Overbought threshold for RSI.
    rsi_oversold (int): Oversold threshold for RSI.

    Returns:
    pd.DataFrame: DataFrame with additional 'Signal' column where 1 = buy signal, -1 = sell signal, 0 = hold.
    """
    # Compute the MACD and Signal Line
    df['EMA_short'] = df['Close'].ewm(span=short_window, adjust=False).mean()
    df['EMA_long'] = df['Close'].ewm(span=long_window, adjust=False).mean()
    df['MACD'] = df['EMA_short'] - df['EMA_long']
    df['Signal_Line'] = df['MACD'].ewm(span=signal_window, adjust=False).mean()

    # Compute RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=rsi_window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_window).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # Generate preliminary MACD signals
    df['MACD_Signal'] = 0
    df.loc[(df['MACD'] > df['Signal_Line']) & (df['MACD'].shift(1) <= df['Signal_Line'].shift(1)), 'MACD_Signal'] = 1
    df.loc[(df['MACD'] < df['Signal_Line']) & (df['MACD'].shift(1) >= df['Signal_Line'].shift(1)), 'MACD_Signal'] = -1

    # Confirm signals with RSI
    df['Signal'] = 0
    df.loc[(df['MACD_Signal'] == 1) & (df['RSI'] < rsi_oversold), 'Signal'] = 1
    df.loc[(df['MACD_Signal'] == -1) & (df['RSI'] > rsi_overbought), 'Signal'] = -1

    # Drop intermediate columns
    df.drop(['EMA_short', 'EMA_long', 'MACD_Signal', 'RSI'], axis=1, inplace=True)

    return df

def plot_signals(df):
    """
    Plot the buy/sell signals on the price chart with MACD and Signal Line.

    Parameters:
    df (pd.DataFrame): DataFrame with OHLCV data and 'Signal' column
    """
    fig, (ax1, ax2) = plt.subplots(2, figsize=(12, 8), sharex=True)

    # Plotting the close price
    ax1.plot(df['Close'], label='Close Price')
    ax1.plot(df[df['Signal'] == 1].index, df[df['Signal'] == 1]['Close'], '^', markersize=10, color='g', lw=0, label='Buy Signal')
    ax1.plot(df[df['Signal'] == -1].index, df[df['Signal'] == -1]['Close'], 'v', markersize=10, color='r', lw=0, label='Sell Signal')
    ax1.set_title('Close Price with Buy/Sell Signals')
    ax1.legend()

    # Plotting the MACD and Signal Line
    ax2.plot(df['MACD'], label='MACD', color='b')
    ax2.plot(df['Signal_Line'], label='Signal Line', color='orange')
    ax2.set_title('MACD and Signal Line')
    ax2.legend()

    plt.show()

# Example usage
# Assuming `data` is a DataFrame with OHLCV data
storage = MetatraderSymbolPriceManager(TradingSymbol.XAUUSD)
data = storage.generate_ohlcv(1).dropna()

# data = pd.read_csv('path_to_your_ohlcv_data.csv')
signals = generate_macd_signals(data)
plot_signals(signals)
