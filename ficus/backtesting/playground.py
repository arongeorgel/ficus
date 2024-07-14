import MetaTrader5 as mt5
import time
import pandas as pd
import numpy as np

# Initialize MetaTrader 5
if not mt5.initialize():
    print("MetaTrader5 initialization failed")
    mt5.shutdown()

# Define the symbol
symbol = "XAUUSD"

# Ensure the symbol is available
if not mt5.symbol_select(symbol, True):
    print(f"Failed to select {symbol}")
    mt5.shutdown()

# Function to get the latest tick data
def get_latest_tick(symbol):
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        print(f"Failed to get tick data for {symbol}")
    return tick

# Function to get the latest OHLC data for the last 5 minutes
def get_ohlc_data(symbol):
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 50)  # 5-minute timeframe
    if rates is None or len(rates) == 0:
        print(f"Failed to get OHLC data for {symbol}")
        return pd.DataFrame()
    return pd.DataFrame(rates)

# Function to calculate MACD
def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    short_ema = data['close'].ewm(span=short_window, adjust=False).mean()
    long_ema = data['close'].ewm(span=long_window, adjust=False).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=signal_window, adjust=False).mean()

    data['MACD'] = macd
    data['Signal'] = signal
    data['Position'] = np.where((data['MACD'] > data['Signal']) & (data['MACD'].shift(1) <= data['Signal'].shift(1)), 1,
                                np.where((data['MACD'] < data['Signal']) & (
                                        data['MACD'].shift(1) >= data['Signal'].shift(1)), -1, 0))

    return data

# Function to check your custom signals using MACD strategy
def check_signals(tick, ohlc_data):
    if ohlc_data is not None and not ohlc_data.empty:
        ohlc_data = calculate_macd(ohlc_data)

        position = ohlc_data['Position'].iloc[-1]
        if position == 1:
            return {"action": "buy", "volume": 0.1}
        elif position == -1:
            return {"action": "sell", "volume": 0.1}

    return {"action": "hold"}

# Function to execute trades based on signals
def execute_trade(signal):
    tick = mt5.symbol_info_tick(symbol)
    price = tick.ask if signal['action'] == "buy" else tick.bid
    stop_loss = price - 80 if signal['action'] == "buy" else price + 80
    take_profit2 = price + 100 if signal['action'] == "buy" else price - 100

    if signal['action'] == "buy":
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": signal['volume'],
            "type": mt5.ORDER_TYPE_BUY,
            "price": price,
            "sl": stop_loss,
            "tp": take_profit2,
            "deviation": 10,
            "magic": 234000,
            "comment": "Python script open",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        result = mt5.order_send(request)
        print(result)

    elif signal['action'] == "sell":
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": signal['volume'],
            "type": mt5.ORDER_TYPE_SELL,
            "price": price,
            "sl": stop_loss,
            "tp": take_profit2,
            "deviation": 10,
            "magic": 234000,
            "comment": "Python script open",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        result = mt5.order_send(request)
        print(result)

# Function to manage positions
def manage_positions():
    positions = mt5.positions_get(symbol=symbol)
    if positions:
        print(f"Currently holding {len(positions)} position(s)")
        print(positions)
        for position in positions:
            tick = mt5.symbol_info_tick(symbol)
            price = tick.bid if position.type == mt5.ORDER_TYPE_BUY else tick.ask

            # Check if first take profit level is hit
            if ((position.type == mt5.ORDER_TYPE_BUY and price >= position.price_open + 70)
                    or (position.type == mt5.ORDER_TYPE_SELL and price <= position.price_open - 70)):
                # Close half the position
                print(f"price {position.price_open} is higher than tp1 {position.price_open + 70}")
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": symbol,
                    "volume": round(position.volume / 2, 2),
                    "type": mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                    "position": position.ticket,
                    "price": price,
                    "deviation": 10,
                    "magic": 234000,
                    "comment": "Python script partial close",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_FOK,
                }
                result = mt5.order_send(request)
                print(result)

                # Update stop loss to entry point for the remaining position
                new_stop_loss = position.price_open
                request = {
                    "action": mt5.TRADE_ACTION_SLTP,
                    "position": position.ticket,
                    "sl": new_stop_loss,
                    "tp": position.tp,
                }
                result = mt5.order_send(request)
                print(result)

# Main loop to run 24/5
previous_tick = get_latest_tick(symbol)
if previous_tick is None:
    previous_tick = mt5.symbol_info_tick(symbol)
last_ohlc_fetch_time = time.time()

while True:
    # Get the latest tick data every 2 seconds
    latest_tick = get_latest_tick(symbol)

    # Check if the latest tick is valid and there's a new tick
    if latest_tick is not None and (previous_tick is None or latest_tick.time != previous_tick.time):
        # Check for signals based on the latest tick
        ohlc_data = None
        if time.time() - last_ohlc_fetch_time >= 60:  # 300 seconds = 5 minutes
            ohlc_data = get_ohlc_data(symbol)
            last_ohlc_fetch_time = time.time()

        signal = check_signals(latest_tick, ohlc_data)

        # Execute trades based on signals
        execute_trade(signal)

        # Manage positions to handle partial closes and stop loss updates
        manage_positions()

        # Update the previous tick
        previous_tick = latest_tick

    # Wait a short time before checking again
    time.sleep(2)

    # Check the time to ensure it runs only during market hours (24/5)
    current_time = pd.Timestamp.now(tz='UTC')
    if current_time.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        print("Market closed, sleeping until Monday...")
        while current_time.weekday() >= 5:
            time.sleep(3600)  # Sleep for an hour before rechecking
            current_time = pd.Timestamp.now(tz='UTC')

# Shutdown MetaTrader 5
mt5.shutdown()
