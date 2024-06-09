import matplotlib.pyplot as plt
import yfinance as yf

from ficus.g.test_backtesting import backtest_strategy



def plot_combined_signals(df, ema_window):
    plt.figure(figsize=(10, 6))

    # Price and EMA
    plt.subplot(1, 1, 1)
    plt.plot(df['Close'], label='Close Price')
    plt.plot(df[f'ema_{ema_window}'], label=f'EMA {ema_window}')
    plt.scatter(df[df['Position'] == 1].index, df[df['Position'] == 1]['Close'], marker='^', color='green', label='Buy Signal', alpha=1)
    plt.scatter(df[df['Position'] == -1].index, df[df['Position'] == -1]['Close'], marker='v', color='red', label='Sell Signal', alpha=1)
    plt.title('Price and Trading Signals')
    plt.legend()

    plt.tight_layout()
    plt.show()

# Download Forex data
ticker = 'GC=F'
start_date = '2024-06-03'
end_date = '2024-06-08'
interval = '5m'

forex_data = yf.download(ticker, start=start_date, end=end_date, interval=interval)

ema_window = 50  # Example long-term EMA window

forex_data = calculate_ema(forex_data, ema_window)
forex_data = add_combined_signals(forex_data, ema_window)
ema_capital = backtest_strategy(forex_data, [3, 5, 10, 20])
print(f"macd capital = {ema_capital}")

plot_combined_signals(forex_data, ema_window)
