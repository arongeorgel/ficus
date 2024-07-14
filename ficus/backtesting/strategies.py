# Function to implement the moving average crossover strategy
import numpy as np
import ta


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


def strategy_macd4(data, short_window=12, long_window=26, signal_window=19):
    short_ema = data['Close'].ewm(span=short_window, adjust=False).mean()
    long_ema = data['Close'].ewm(span=long_window, adjust=False).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=signal_window, adjust=False).mean()

    data['MACD'] = macd
    data['Signal'] = signal
    data['Position'] = np.where((data['MACD'] > data['Signal']) & (data['MACD'].shift(1) <= data['Signal'].shift(1)), 1,
                                np.where((data['MACD'] < data['Signal']) & (
                                            data['MACD'].shift(1) >= data['Signal'].shift(1)), -1, 0))

    return data


def strategy_macd3(df, short_window=12, long_window=26):
    df[f'ema_{short_window}'] = df['Close'].ewm(span=short_window, adjust=False).mean()
    df[f'ema_{long_window}'] = df['Close'].ewm(span=long_window, adjust=False).mean()
    # MACD
    macd = ta.trend.MACD(df['Close'])
    df['MACD'] = macd.macd()
    df['Signal_Line'] = macd.macd_signal()
    df['MACD_Diff'] = df['MACD'] - df['Signal_Line']

    # RSI
    df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()

    # Bollinger Bands
    bollinger = ta.volatility.BollingerBands(df['Close'], window=20, window_dev=2)
    df['Bollinger_High'] = bollinger.bollinger_hband()
    df['Bollinger_Low'] = bollinger.bollinger_lband()

    df['Position'] = 0
    buy_condition = (df['MACD'] > df['Signal_Line']) & (df['RSI'] < 70) & (df['Close'] < df['Bollinger_High'])
    sell_condition = (df['MACD'] < df['Signal_Line']) & (df['RSI'] > 30) & (df['Close'] > df['Bollinger_Low'])
    df.loc[buy_condition, 'Position'] = 1
    df.loc[sell_condition, 'Position'] = -1

    # df['Position'] = df['Signal'].diff()
    # df['Position'] = df['Position'].apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
    return df


def strategy_macd2(data, short_window=12, long_window=26, signal_window=10, smoothing_window=10):
    data[f'ema_{short_window}'] = data['Close'].ewm(span=short_window, adjust=False).mean()
    data[f'ema_{long_window}'] = data['Close'].ewm(span=long_window, adjust=False).mean()
    data['MACD'] = data[f'ema_{short_window}'] - data[f'ema_{long_window}']
    data['Signal_Line'] = data['MACD'].ewm(span=signal_window, adjust=False).mean()

    # Apply smoothing
    data['MACD_Smooth'] = data['MACD'].rolling(window=smoothing_window).mean()
    data['Signal_Smooth'] = data['Signal_Line'].rolling(window=smoothing_window).mean()

    # Generate signals
    data['Signal'] = 0
    data['Signal'][short_window:] = np.where(data['MACD_Smooth'][short_window:] > data['Signal_Smooth'][short_window:],
                                             1, -1)
    data['Position'] = data['Signal'].diff()
    data['Position'] = data['Position'].apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))

    return data


def strategy_macd(df, ema_window, short_window=10, long_window=26, signal_window=9):
    # Calculate EMAs
    df[f'ema_{ema_window}'] = df['Close'].ewm(span=ema_window, adjust=False).mean()
    df[f'ema_{short_window}'] = df['Close'].ewm(span=short_window, adjust=False).mean()
    df[f'ema_{long_window}'] = df['Close'].ewm(span=long_window, adjust=False).mean()
    ema_short = df['Close'].ewm(span=short_window, adjust=False).mean()
    ema_long = df['Close'].ewm(span=long_window, adjust=False).mean()
    macd = ema_short - ema_long
    signal_line = macd.ewm(span=signal_window, adjust=False).mean()

    # Initialize Position column
    df['Position'] = 0

    # Create buy and sell signals
    buy_signal = (macd > signal_line) & (macd.shift(1) <= signal_line.shift(1))
    sell_signal = (macd < signal_line) & (macd.shift(1) >= signal_line.shift(1))

    # Confirm trend with EMA
    uptrend = df['Close'] > df[f'ema_{ema_window}']
    downtrend = df['Close'] < df[f'ema_{ema_window}']

    df.loc[buy_signal & uptrend, 'Position'] = 1
    df.loc[sell_signal & downtrend, 'Position'] = -1

    df['MACD'] = macd
    df['Signal_Line'] = signal_line

    return df
