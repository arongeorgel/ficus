import yfinance as yf


def get_usd_conversion_rate(symbol):
    pair = 'USD' + symbol[3:] + '=X'  # Convert to Yahoo Finance ticker format
    print(f"download for {pair}")
    data = yf.download(pair, period='1d')
    return data['Close'].iloc[-1]


def forex_calculator(action, symbol, entry, sl, account_balance, risk_percentage, contract_size, usd_conversion_rate):
    if symbol == 'XAUUSD':
        contract_size = 100

    if symbol.endswith('USD'):
        # Direct USD pair
        pip_value_usd = (sl - entry) * contract_size
    elif symbol.endswith('JPY'):
        # JPY pair
        pip_value_jpy = (sl - entry) * contract_size
        pip_value_usd = pip_value_jpy / usd_conversion_rate
    else:
        # Cross-currency pair
        pip_value_cross = (sl - entry) * contract_size
        pip_value_usd = pip_value_cross / usd_conversion_rate

    pip_value_usd = abs(pip_value_usd)

    # Calculate the risk amount in USD
    risk_amount_usd = (risk_percentage / 100) * account_balance

    # Calculate the lot size
    lots = risk_amount_usd / pip_value_usd

    # Calculate the units
    units = lots * contract_size

    return round(lots, 4), round(units, 3), round(risk_amount_usd, 2)


# Input values
account_balance = 2000
risk_percentage = 2
contract_size = 100000

# Example trades
trades = [
    {'action': 'buy', 'symbol': 'NZDCAD', 'entry': 0.816, 'sl': 0.806},
    {'action': 'sell', 'symbol': 'XAUUSD', 'entry': 2301.0, 'sl': 2310.0},
    {'action': 'buy', 'symbol': 'EURUSD', 'entry': 1.07645, 'sl': 1.06645},
    {'action': 'sell', 'symbol': 'EURJPY', 'entry': 164.335, 'sl': 165.335},
    {'action': 'sell', 'symbol': 'AUDNZD', 'entry': 1.0962, 'sl': 1.1062},

    {'action': 'sell', 'symbol': 'GBPUSD', 'entry': 1.2768, 'sl': 1.2838},
    {'action': 'sell', 'symbol': 'GBPCAD', 'entry': 1.7436, 'sl': 1.7516},
    {'action': 'sell', 'symbol': 'GBPJPY', 'entry': 199.33, 'sl': 200.0},
    {'action': 'buy', 'symbol': 'USDCHF', 'entry': 0.9069, 'sl': 0.8982},#87
    {'action': 'buy', 'symbol': 'CADCHF', 'entry': 0.6684, 'sl': 0.6584}, #100

]

# Process each trade
for trade in trades:
    # usd_conversion_rate = usd_conversion_rates[trade['symbol'][:3] + 'USD']  # Use appropriate conversion rate
    usd_conversion_rate = get_usd_conversion_rate(trade['symbol'])
    lots, units, money_at_risk = forex_calculator(
        trade['action'], trade['symbol'], trade['entry'], trade['sl'], account_balance, risk_percentage, contract_size, usd_conversion_rate
    )
    print(f"Trade: {trade}")
    print(f"USD conversion rate: {usd_conversion_rate}")
    print(f"Lots (trade size): {lots}")
    print(f"Units (trade size): {units}")
    print(f"Money at risk: US${money_at_risk}")
    print()
