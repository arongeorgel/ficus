# Function to implement the moving average crossover strategy
import numpy as np


def simple_crossover_strategy(data, short_window, long_window):
    # Calculate the short and long moving averages
    data['Short_Window'] = data['Close'].rolling(window=short_window, min_periods=1).mean()
    data['Long_Window'] = data['Close'].rolling(window=long_window, min_periods=1).mean()

    # Generate signals
    row_indexer = data.index[short_window:]
    data['Signal'] = 0  # Default to no position
    trading_signal = np.where(data['Short_Window'][short_window:] > data['Long_Window'][short_window:], 1, 0)
    data.loc[row_indexer, 'Signal'] = trading_signal
    data['Position'] = data['Signal'].diff()

    return data


def exponential_crossover_strategy(data, short_window, long_window):
    # Calculate the short and long moving averages
    data['Short_Window'] = data['Close'].ewm(span=short_window, adjust=False).mean()
    data['Long_Window'] = data['Close'].ewm(span=long_window, adjust=False).mean()

    # Generate signals
    row_indexer = data.index[short_window:]
    data['Signal'] = 0  # Default to no position
    trading_signal = np.where(data['Short_Window'][short_window:] > data['Long_Window'][short_window:], 1, 0)
    data.loc[row_indexer, 'Signal'] = trading_signal
    data['Position'] = data['Signal'].diff()

    return data


def calculate_macd(data, fast_period=12, slow_period=26, signal_period=9):
    # Calculate the MACD and Signal Line
    short_ema = data['Close'].ewm(span=fast_period, adjust=False).mean()
    long_ema = data['Close'].ewm(span=slow_period, adjust=False).mean()
    macd = short_ema - long_ema
    signal_line = macd.ewm(span=signal_period, adjust=False).mean()
    return macd, signal_line


def macd_crossover_strategy(data, fast_period=12, slow_period=26, signal_period=9):
    # Calculate the MACD and Signal Line
    short_ema = data['Close'].ewm(span=fast_period, adjust=False).mean()
    long_ema = data['Close'].ewm(span=slow_period, adjust=False).mean()
    macd = short_ema - long_ema
    signal_line = macd.ewm(span=signal_period, adjust=False).mean()

    # Initialize position array with 'None'
    position = [None] * len(macd)

    # Generate signals
    for i in range(1, len(macd)):
        if macd[i] > signal_line[i] and macd[i - 1] <= signal_line[i - 1]:
            position[i] = 1
        elif macd[i] < signal_line[i] and macd[i - 1] >= signal_line[i - 1]:
            position[i] = -1

    # Add 'position' to the DataFrame
    data['Position'] = position

    return data