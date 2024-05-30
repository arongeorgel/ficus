import threading
import time
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.animation import FuncAnimation

from ficus.g.strategies import simple_crossover_strategy
from test_backtesting import download_forex_data, now_trading

# Initialize global data
data = pd.DataFrame(columns=['Datetime', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'])

# Function to initialize the plot
def init():
    ax.set_title('Price and Buy/Sell Signals')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    return ln,

# Function to update the plot
def update(frame):
    global data

    # Ensure data exists
    if data.empty:
        return ln,

    # Calculate strategic data
    strategic_data = simple_crossover_strategy(data, 20, 50)
    for _, row in strategic_data.tail(1).iterrows():
        now_trading(row, [20, 50, 90, 120])

    # Clear previous data
    ax.clear()

    # plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    # plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))

    # Plot the close price and moving averages
    ax.plot(strategic_data['Datetime'], strategic_data['Close'], label='Close Price', alpha=0.5)
    ax.plot(strategic_data['Datetime'], strategic_data['Long_Window'], label='SMA Long', alpha=0.5)
    ax.plot(strategic_data['Datetime'], strategic_data['Short_Window'], label='SMA Short', alpha=0.5)

    # Plot buy and sell signals
    buy_signals = strategic_data[strategic_data['Position'] == 1]
    sell_signals = strategic_data[strategic_data['Position'] == -1]
    ax.scatter(buy_signals['Datetime'], buy_signals['Close'], marker='^', color='g', label='Buy Signal')
    ax.scatter(sell_signals['Datetime'], sell_signals['Close'], marker='v', color='r', label='Sell Signal')

    ax.set_title('Price and Buy/Sell Signals')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.legend()

    return ax.lines + [ax.collections[0], ax.collections[1]]  # Return all plotted elements


# Callback function to receive new data
def on_message(new_data):
    global data
    # Concatenate the new data with the existing data
    new_data_df = pd.DataFrame([new_data])
    data = pd.concat([data, new_data_df], ignore_index=True)


# Function to emit new data every second in a separate thread
def emit_data(forex_data):
    for _, row in forex_data.iterrows():
        on_message(row)
        time.sleep(1)


# Main script
if __name__ == "__main__":
    # Download the forex data
    forex_data = download_forex_data("GC=F", '2024-05-27', '2024-05-30', '5m')
    # Start the data emission thread
    emit_thread = threading.Thread(target=emit_data, args=(forex_data,))
    emit_thread.start()

    # from here down, handle the plot chart
    # Create the plot
    fig, ax = plt.subplots(figsize=(14, 8))
    ln, = ax.plot([], [], 'b-', animated=True)

    # Start the animation
    ani = FuncAnimation(fig, update, init_func=init, blit=True, interval=1100, repeat=False)

    # Show the plot in a non-blocking way
    plt.show(block=True)

    # Join the thread to wait for its completion
    emit_thread.join()
