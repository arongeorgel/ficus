import math

from colorama import init

init()

nr_columns = 3
nr_rows = 3


def calculate_optimal_grid_size(elements_length):
    best_diff = elements_length
    best_rows = 1
    best_cols = elements_length

    global nr_columns
    global nr_rows

    # Iterate over possible number of rows
    for rows in range(1, int(math.sqrt(elements_length)) + 1):
        if elements_length % rows == 0:
            cols = elements_length // rows
            diff = abs(rows - cols)
            if diff < best_diff:
                best_diff = diff
                best_rows = rows
                best_cols = cols

    nr_columns = best_cols
    nr_rows = best_rows


def plot_sma(plotter, data, windows):
    plotter.subplot(2, 2, 1)
    plotter.plot(data['Datetime'], data['Close'], label='Close Price', alpha=0.5)
    plotter.plot(data['Datetime'], data['Long_Window'], label=f'SMA {windows[0]}', alpha=0.5)
    plotter.plot(data['Datetime'], data['Short_Window'], label=f'SMA {windows[1]}', alpha=0.5)
    # Plot markers for position open (buy)
    buy_signals = data[data['Position'] == 1]
    plotter.scatter(buy_signals['Datetime'], buy_signals['Close'], marker='^', color='g', label='Buy Signal')

    # Plot markers for position close (sell)
    sell_signals = data[data['Position'] == -1]
    plotter.scatter(sell_signals['Datetime'], sell_signals['Close'], marker='v', color='r', label='Sell Signal')

    plotter.title('SMA Buy/Sell')
    plotter.legend(loc='upper left')


def plot_ema(plotter, data, windows):
    plotter.subplot(2, 2, 2)
    plotter.plot(data['Datetime'], data['Close'], label='Close Price', alpha=0.5)
    plotter.plot(data['Datetime'], data['Long_Window'], label=f'EMA {windows[0]}', alpha=0.5)
    plotter.plot(data['Datetime'], data['Short_Window'], label=f'EMA {windows[1]}', alpha=0.5)
    # Plot markers for position open (buy)
    buy_signals = data[data['Position'] == 1]
    plotter.scatter(buy_signals['Datetime'], buy_signals['Close'], marker='^', color='g', label='Buy Signal')

    # Plot markers for position close (sell)
    sell_signals = data[data['Position'] == -1]
    plotter.scatter(sell_signals['Datetime'], sell_signals['Close'], marker='v', color='r', label='Sell Signal')
    plotter.title('EMA Buy/Sell')
    plotter.legend(loc='upper left')


def plot_macd(symbol, plt, data, short_window=12, long_window=26, plt_index=0):
    """
    The window has a 3 by 3 configuration, use plt_index to display in a given area

    :param symbol
    :param plt:
    :param data:
    :param ema_window:
    :param plt_index:
    :return:
    """
    plt.subplot(2, 1, 1)

    # Unpack data for easier use
    dates = data['Datetime']
    opens = data['Open']
    closes = data['Close']
    highs = data['High']
    lows = data['Low']

    colors = ['green' if close > open else 'red' for close, open in zip(closes, opens)]

    num_bars = len(dates)
    bar_width = (dates.max() - dates.min()) / (num_bars * 3)  # Adjust multiplier for desired width
    plt.bar(dates, closes - opens, bottom=opens, color=colors, width=bar_width)

    plt.vlines(dates, lows, highs, color=colors, linewidth=1)

    # plt.plot(data['Datetime'], data[f'ema_{short_window}'], label=f'EMA {short_window}', alpha=0.5)
    # plt.plot(data['Datetime'], data['Close'], label=f'EMA {long_window}', alpha=0.5)
    plt.scatter(data[data['Position'] == 1]['Datetime'], data[data['Position'] == 1]['Close'], marker='^', color='purple', label='Buy Signal', alpha=1)
    plt.scatter(data[data['Position'] == -1]['Datetime'], data[data['Position'] == -1]['Close'], marker='v', color='orange', label='Sell Signal', alpha=1)
    plt.grid()

    # Plot MACD and signal line
    plt.subplot(2, 1, 2)
    plt.plot(data['Datetime'], data['MACD'], label='MACD', color='blue')
    plt.plot(data['Datetime'], data['Signal_Line'], label='Signal Line', color='red')

    plt.title(f'MACD Strategy on {symbol}')
    plt.legend()


def plot_candlesticks(plt, data, plt_index):
    """
    Plots candlesticks from OHLC data in a pandas DataFrame.

    Args:
        plt: the plot chart
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
    plt.subplot(nr_rows, nr_columns, plt_index)
    num_bars = len(dates)
    bar_width = (dates.max() - dates.min()) / (num_bars * 2)  # Adjust multiplier for desired width
    plt.bar(dates, closes - opens, bottom=opens, color=colors, width=bar_width)

    plt.vlines(dates, lows, highs, color=colors, linewidth=1)
    plt.xticks(rotation=45)  # Rotate x-axis labels for readability
    plt.grid(True, linestyle='--', linewidth=0.5)

    plt.xlabel('Date')
    plt.ylabel('Price')

    plt.title('Candlestick Chart')
    plt.tight_layout()
