from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf
from colorama import init
from matplotlib import pyplot as plt

from ficus.g.strategies import macd_crossover_strategy, calculate_macd, simple_crossover_strategy, \
    exponential_crossover_strategy

# Initialize colorama
init()


def generate_weekly_windows(start_date, end_date):
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    current_start = start_date
    windows = []

    while current_start < end_date:
        current_end = min(current_start + timedelta(days=6), end_date)
        windows.append((current_start.strftime("%Y-%m-%d"), current_end.strftime("%Y-%m-%d")))
        current_start = current_start + timedelta(days=7)

    return windows


# Function to download Forex data
def download_forex_data(ticker, start_date_str, end_date_str, interval):
    if interval == '1m':
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


# Initial capital
initial_capital = 4000
capital = initial_capital

# Position: 0 = No position, 1 = Long, -1 = Short
current_position = 0
entry_price = 0
volume = 0.09

stop_loss_distance = 10.0  # Fixed stop loss distance
take_profits = []
stop_loss = 0
stop_loss_dollars = 0
first_take_profit = 0


def now_trading(data_row, profit_pips):
    global initial_capital
    global capital
    global current_position
    global entry_price
    global volume
    global stop_loss_distance
    global take_profits
    global stop_loss
    global stop_loss_dollars
    global first_take_profit

    signal = data_row['Position']
    if pd.isna(signal):
        return

    # Close current position if there's a signal change
    if current_position != 0 and signal != 0 and signal != current_position:
        if current_position == 1:
            result = calculate_dollars(data_row['Close'] - entry_price, volume)
        else:
            result = calculate_dollars(entry_price - data_row['Close'], volume)

        capital += result
        # print(
        #     f"{Fore.RED if result < 0 else Fore.GREEN}"
        #     f"New signal. Closing {'long' if current_position == 1 else 'short'} position "
        #     f"at price {data_row['Close']:.2f}. Gain/Loss: ${result:.2f}, Updated Capital: ${capital:.2f}"
        #     f"{Style.RESET_ALL}")
        current_position = 0

        # Open a new position if there is no current position

    # Based on the signal, buy or sell
    if current_position == 0 and signal != 0:
        current_position = signal
        entry_price = data_row['Close']
        stop_loss_dollars = calculate_dollars(stop_loss_distance, volume)
        stop_loss, take_profits = calculate_sl_and_tp(signal, stop_loss_distance, profit_pips)
        first_take_profit = take_profits[0]

        # take_profits_string = "\n".join([f"TP{i + 1}: {tp[0]:.2f} (${tp[1]:.2f})" for i, tp in enumerate(take_profits)])
        # print(
        #     "\n-----------------------------------------------------------------------\n"
        #     f"With {capital:.2f} capital, opening {'long' if signal == 1 else 'short'} "
        #     f"position at price {entry_price:.2f}.\n"
        #     f"SL: {stop_loss:.2f} (${stop_loss_dollars:.2f})\n{take_profits_string}\n"
        #     f"Volume: {volume}")

        # Check for take profit or stop loss conditions

    # At every tick, check next step (close, half close, take profit, etc.)
    if current_position != 0:
        tp_hit = False
        for tp, tp_diff in take_profits.copy():
            if (current_position == 1 and data_row['High'] >= tp) or (current_position == -1 and data_row['Low'] <= tp):
                capital += tp_diff
                take_profits.remove((tp, tp_diff))
                tp_hit = True
                # print(
                #     f"{Fore.GREEN}Take profit hit on {'long' if current_position == 1 else 'short'} position "
                #     f"at price {tp:.2f} (+${tp_diff:.2f}).{Style.RESET_ALL}")

                # Reduce the traded volume by half
                # volume /= 2

                # Set the stop loss to the entry price after hitting the first take profit
                if not take_profits:  # If no take profits left, we're at the last take profit level
                    stop_loss = first_take_profit
                    # TODO calculate stop dollars here
                elif len(take_profits) == 1:
                    stop_loss = entry_price
                    stop_loss_dollars = 0

                if not take_profits:
                    current_position = 0
                    break

        if not tp_hit:
            if (current_position == 1 and data_row['Low'] <= stop_loss) or (
                    current_position == -1 and data_row['High'] >= stop_loss):
                capital -= stop_loss_dollars
                # print(
                #     f"{Fore.RED}Stop loss hit on {'long' if current_position == 1 else 'short'} position "
                #     f"at price {stop_loss:.2f} (-${stop_loss_dollars:.2f}){Style.RESET_ALL}")
                current_position = 0


def calculate_sl_and_tp(signal, entry, sl_distance, profit_pips):
    sl = entry - sl_distance if signal == 1 else entry + sl_distance
    tp = [(entry + tp * 0.1 if signal == 1 else entry - tp * 0.1, calculate_dollars(tp * 0.1, volume)) for tp in profit_pips]
    return sl, tp


def backtest_strategy(data, profit_pips):
    global initial_capital
    global capital
    global current_position
    global entry_price
    global volume
    global stop_loss_distance
    global take_profits
    global stop_loss
    global stop_loss_dollars
    global first_take_profit

    # Initial capital
    initial_capital = 100000
    capital = initial_capital

    # Position: 0 = No position, 1 = Long, -1 = Short
    current_position = 0
    entry_price = 0
    volume = 5

    stop_loss_distance = 10.0  # Fixed stop loss distance
    take_profits = []
    stop_loss = 0
    stop_loss_dollars = 0
    first_take_profit = 0

    for index, row in data.iterrows():
        now_trading(row, profit_pips)

    return capital


def plot_macd(plt, data):
    macd, signal_line = calculate_macd(data)
    data['MACD'] = macd
    data['Signal_Line'] = signal_line

    plt.subplot(2, 2, 1)
    plt.plot(data['Datetime'], data['Close'], label='Close Price', color='blue', alpha=0.5)
    # Plot markers for position open (buy)
    buy_signals = data[data['Position'] == 1]
    plt.scatter(buy_signals['Datetime'], buy_signals['Close'], marker='^', color='g', label='Buy Signal')

    # Plot markers for position close (sell)
    sell_signals = data[data['Position'] == -1]
    plt.scatter(sell_signals['Datetime'], sell_signals['Close'], marker='v', color='r', label='Sell Signal')

    plt.title('MACD Buy/Sell')
    plt.legend(loc='upper left')

    # Plot MACD and Signal Line
    plt.subplot(2, 2, 3)
    plt.plot(data['Datetime'], data['MACD'], label='MACD', color='blue', alpha=0.35)
    plt.plot(data['Datetime'], data['Signal_Line'], label='Signal Line', color='red', alpha=0.35)
    plt.title('MACD & Signal Line')
    plt.legend(loc='upper left')


def plot_sma(plt, data):
    plt.subplot(2, 2, 2)
    plt.plot(data['Datetime'], data['Close'], label='Close Price', alpha=0.5)
    plt.plot(data['Datetime'], data['Long_Window'], label='SMA 20', alpha=0.5)
    plt.plot(data['Datetime'], data['Short_Window'], label='SMA 100', alpha=0.5)
    # Plot markers for position open (buy)
    buy_signals = data[data['Position'] == 1]
    plt.scatter(buy_signals['Datetime'], buy_signals['Close'], marker='^', color='g', label='Buy Signal')

    # Plot markers for position close (sell)
    sell_signals = data[data['Position'] == -1]
    plt.scatter(sell_signals['Datetime'], sell_signals['Close'], marker='v', color='r', label='Sell Signal')

    plt.title('SMA Buy/Sell')
    plt.legend(loc='upper left')


def plot_ema(plt, data, windows):
    # plt.subplot(2, 2, 4)
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


def main():
    # ticker = 'USDEUR=X'
    ticker = 'GC=F'
    # ticker = 'BTC=F'

    plt.figure(figsize=(14, 7))

    # Download data
    forex_data = download_forex_data(ticker, '2024-05-01', '2024-05-29', '5m')


    # Apply SMA strategy
    strategy_two = simple_crossover_strategy(forex_data, 20, 50)
    sma_capital = backtest_strategy(strategy_two, [20, 50, 90, 140])
    print(f"SMA capital = {sma_capital}")
    plot_sma(plt, strategy_two)

    # Apply EMA strategy
    strategy_three = exponential_crossover_strategy(forex_data, 20, 50)
    ema_capital = backtest_strategy(strategy_three, [20, 50, 90, 140])
    print(f"EMA capital = {ema_capital}")
    plot_ema(plt, strategy_three)

    # Apply MACD strategy
    strategy_one = macd_crossover_strategy(forex_data, 16, 26, 9)
    mac_capital = backtest_strategy(strategy_one, [5, 10, 20, 35])
    print(f"MACD capital = {mac_capital}")
    plot_macd(plt, forex_data)


    # Formatting
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()
