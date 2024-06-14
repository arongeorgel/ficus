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


def plot_macd(plt, df, ema_window):
    plt.subplot(2, 2, 3)
    plt.plot(df['Datetime'], df['Close'], label='Close Price', alpha=0.5)
    plt.plot(df['Datetime'], df[f'ema_{ema_window}'], label=f'EMA {ema_window}', alpha=0.5)
    plt.scatter(df[df['Position'] == 1]['Datetime'], df[df['Position'] == 1]['Close'], marker='^', color='green', label='Buy Signal', alpha=1)
    plt.scatter(df[df['Position'] == -1]['Datetime'], df[df['Position'] == -1]['Close'], marker='v', color='red', label='Sell Signal', alpha=1)

    plt.title('MACD Strategy')
    plt.legend()
