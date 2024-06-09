import multiprocessing as mp
import time
import pandas as pd
import matplotlib.pyplot as plt
from ficus.g.strategies import strategy_simple_crossover
from test_backtesting import download_forex_data, now_trading

class ProcessPlotter:
    def __init__(self):
        self.data = pd.DataFrame(columns=['Datetime', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'])
        self.terminate_plot = False
        self.plot_initialized = False

    def terminate(self):
        plt.close('all')

    def call_back(self):
        while self.pipe.poll():
            command = self.pipe.recv()
            if command is None:
                self.terminate()
                return False
            else:
                if not self.plot_initialized:
                    self.init_plot()
                    self.plot_initialized = True
                self.data = pd.concat([self.data, pd.DataFrame([command], columns=self.data.columns)], ignore_index=True)
                self.update_plot()
        self.fig.canvas.draw()
        return True

    def init_plot(self):
        self.fig, self.ax = plt.subplots(figsize=(14, 8))
        self.ax.set_title('Price and Buy/Sell Signals')
        self.ax.set_xlabel('Date')
        self.ax.set_ylabel('Price')

    def update_plot(self):
        strategic_data = strategy_simple_crossover(self.data, 20, 50)
        for _, row in strategic_data.tail(1).iterrows():
            now_trading(row, [20, 50, 90, 120])

        self.ax.clear()
        self.ax.plot(strategic_data['Datetime'], strategic_data['Close'], label='Close Price', alpha=0.5)
        self.ax.plot(strategic_data['Datetime'], strategic_data['Long_Window'], label='SMA Long', alpha=0.5)
        self.ax.plot(strategic_data['Datetime'], strategic_data['Short_Window'], label='SMA Short', alpha=0.5)

        buy_signals = strategic_data[strategic_data['Position'] == 1]
        sell_signals = strategic_data[strategic_data['Position'] == -1]
        self.ax.scatter(buy_signals['Datetime'], buy_signals['Close'], marker='^', color='g', label='Buy Signal')
        self.ax.scatter(sell_signals['Datetime'], sell_signals['Close'], marker='v', color='r', label='Sell Signal')

        self.ax.set_title('Price and Buy/Sell Signals')
        self.ax.set_xlabel('Date')
        self.ax.set_ylabel('Price')
        self.ax.legend()

    def __call__(self, pipe):
        print('Starting plotter...')
        self.pipe = pipe
        self.fig, self.ax = plt.subplots()
        timer = self.fig.canvas.new_timer(interval=1000)
        timer.add_callback(self.call_back)
        timer.start()
        plt.show()


class NBPlot:
    def __init__(self):
        self.plot_pipe, plotter_pipe = mp.Pipe()
        self.plotter = ProcessPlotter()
        self.plot_process = mp.Process(target=self.plotter, args=(plotter_pipe,), daemon=True)
        self.plot_process.start()

    def plot(self, data=None, finished=False):
        send = self.plot_pipe.send
        if finished:
            send(None)
        elif data is not None:
            send(data)


def emit_data(forex_data, plotter):
    for _, row in forex_data.iterrows():
        plotter.plot(row)
        time.sleep(1)


def main():
    s = "GC=F"
    d = download_forex_data(s, '2024-05-27', '2024-05-30', '5m')

    pl = NBPlot()
    emit_data(d, pl)
    pl.plot(finished=True)


if __name__ == '__main__':
    if plt.get_backend() == "MacOSX":
        mp.set_start_method("forkserver")
    main()
