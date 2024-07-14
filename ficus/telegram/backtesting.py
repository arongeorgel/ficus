import yfinance as yf

running_trades = list()

def on_trade(trade):
    running_trades.append(trade)

