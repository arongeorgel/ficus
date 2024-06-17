from colorama import init

init()


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


def plot_macd(plt, data, ema_window):
    plt.subplot(2, 2, 3)

    # Unpack data for easier use
    dates = data['Datetime']
    opens = data['Open']
    closes = data['Close']
    highs = data['High']
    lows = data['Low']

    colors = ['green' if close > open else 'red' for close, open in zip(closes, opens)]

    num_bars = len(dates)
    bar_width = (dates.max() - dates.min()) / (num_bars * 5)  # Adjust multiplier for desired width
    # plt.bar(dates, closes - opens, bottom=opens, color=colors, width=bar_width)

    # plt.vlines(dates, lows, highs, color=colors, linewidth=1)
    # plt.xticks(rotation=45)  # Rotate x-axis labels for readability

    plt.plot(data['Datetime'], data['Close'], label='Close Price', alpha=0.5)
    plt.plot(data['Datetime'], data[f'ema_{ema_window}'], label=f'EMA {ema_window}', alpha=0.5)
    plt.scatter(data[data['Position'] == 1]['Datetime'], data[data['Position'] == 1]['Close'], marker='^', color='green', label='Buy Signal', alpha=1)
    plt.scatter(data[data['Position'] == -1]['Datetime'], data[data['Position'] == -1]['Close'], marker='v', color='red', label='Sell Signal', alpha=1)

    plt.title('MACD Strategy')
    plt.legend()


def plot_candlesticks(plt, data):
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
    plt.subplot(2, 2, 1)
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
