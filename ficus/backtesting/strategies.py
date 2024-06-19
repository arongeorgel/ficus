# Function to implement the moving average crossover strategy
import numpy as np


def calculate_rsi(df, window=14):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)

    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    df['RSI'] = rsi
    return df


def calculate_bollinger_bands(df, window=20, num_std_dev=2):
    rolling_mean = df['Close'].rolling(window).mean()
    rolling_std = df['Close'].rolling(window).std()

    df['Bollinger_High'] = rolling_mean + (rolling_std * num_std_dev)
    df['Bollinger_Low'] = rolling_mean - (rolling_std * num_std_dev)

    return df


def strategy_exponential_crossover(data, windows):
    # Calculate the short and long moving averages
    data['Short_Window'] = data['Close'].ewm(span=windows[0], adjust=False).mean()
    data['Long_Window'] = data['Close'].ewm(span=windows[1], adjust=False).mean()

    # Generate signals
    row_indexer = data.index[windows[0]:]
    data['Signal'] = 0  # Default to no position
    trading_signal = np.where(data['Short_Window'][windows[0]:] > data['Long_Window'][windows[0]:], 1, 0)
    data.loc[row_indexer, 'Signal'] = trading_signal
    data['Position'] = data['Signal'].diff()

    return data


def strategy_simple_crossover(data, windows: tuple[int, int]):
    # Calculate the short and long moving averages
    data['Short_Window'] = data['Close'].rolling(window=windows[0], min_periods=1).mean()
    data['Long_Window'] = data['Close'].rolling(window=windows[1], min_periods=1).mean()

    # Generate signals
    row_indexer = data.index[windows[0]:]
    data['Position'] = 0  # Default to no position
    trading_signal = np.where(data['Short_Window'][windows[0]:] > data['Long_Window'][windows[0]:], 1, 0)
    data.loc[row_indexer, 'Position'] = trading_signal
    data['Position'] = data['Position'].diff()

    return data


def calculate_ema(df, window):
    df[f'ema_{window}'] = df['Close'].ewm(span=window, adjust=False).mean()
    return df


def strategy_macd(df, ema_window, short_window=10, long_window=26, signal_window=9):
    ema_short = df['Close'].ewm(span=short_window, adjust=False).mean()
    ema_long = df['Close'].ewm(span=long_window, adjust=False).mean()
    macd = ema_short - ema_long
    signal_line = macd.ewm(span=signal_window, adjust=False).mean()

    df['Position'] = 0

    for i in range(1, len(df)):
        # Uptrend confirmed by EMA
        if df['Close'].iloc[i] > df[f'ema_{ema_window}'].iloc[i]:
            # Buy signal from MACD
            if macd.iloc[i] > signal_line.iloc[i] and macd.iloc[i-1] <= signal_line.iloc[i-1]:
                df.at[df.index[i], 'Position'] = 1  # Buy signal

        # Downtrend confirmed by EMA
        if df['Close'].iloc[i] < df[f'ema_{ema_window}'].iloc[i]:
            # Sell signal from MACD
            if macd.iloc[i] < signal_line.iloc[i] and macd.iloc[i-1] >= signal_line.iloc[i-1]:
                df.at[df.index[i], 'Position'] = -1  # Sell signal

    return df
