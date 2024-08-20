import yfinance as yf

from ficus.metatrader.MetatraderTerminal import MetatraderTerminal


class PositionSizeCalculator:
    def __init__(self):
        # Dictionary of pip values for top 21 currency pairs (assuming standard lot size)
        self.trading_pairs = {
            "XAUUSD": {'contract_size': 100},

            "AUDUSD": {'contract_size': 100000},
            "EURUSD": {'contract_size': 100000},
            "GBPUSD": {'contract_size': 100000},
            "NZDUSD": {'contract_size': 100000},

            "AUDCAD": {'contract_size': 100000},
            "EURCAD": {'contract_size': 100000},
            "GBPCAD": {'contract_size': 100000},
            "NZDCAD": {'contract_size': 100000},
            "USDCAD": {'contract_size': 100000},

            "CADCHF": {'contract_size': 100000},
            "NZDCHF": {'contract_size': 100000},
            "USDCHF": {'contract_size': 100000},
            "GBPCHF": {'contract_size': 100000},

            "AUDNZD": {'contract_size': 100000},
            "EURNZD": {'contract_size': 100000},
            "GBPNZD": {'contract_size': 100000},

            "EURAUD": {'contract_size': 100000},
            "GBPAUD": {'contract_size': 100000},

            "EURGBP": {'contract_size': 100000},

            "NAS100": {'contract_size': 1},
            "BTCUSD": {'contract_size': 1},

            "AUDJPY": {'contract_size': 100000},
            "CADJPY": {'contract_size': 100000},
            "CHFJPY": {'contract_size': 100000},
            "EURJPY": {'contract_size': 100000},
            "GBPJPY": {'contract_size': 100000},
            "NZDJPY": {'contract_size': 100000},
            "USDJPY": {'contract_size': 100000},
        }

    @staticmethod
    def get_usd_conversion_rate(symbol, is_backtesting: bool = True):
        pair = 'USD' + symbol[3:] + '=X'  # Convert to Yahoo Finance ticker format
        if is_backtesting:
            return yf.download(pair, period='1d')['Close'].iloc[-1]
        else:
            return MetatraderTerminal.get_current_price(pair, symbol, "buy")

    def forex_calculator(self, symbol, entry, sl, account_balance, risk_percentage, is_backtesting: bool = True):
        trading_pair = self.trading_pairs[symbol]
        if trading_pair is None:
            print(f'Trading pair {symbol} not supported yet')
            return

        if symbol == 'NAS100':
            pip_value_usd = (sl - entry) * trading_pair['contract_size']
        elif symbol.endswith('USD'):
            # Direct USD pair
            pip_value_usd = (sl - entry) * trading_pair['contract_size']
        elif symbol.endswith('JPY'):
            # JPY pair
            pip_value_jpy = (sl - entry) * trading_pair['contract_size']
            pip_value_usd = pip_value_jpy / self.get_usd_conversion_rate(symbol, is_backtesting)
        else:
            # Cross-currency pair
            pip_value_cross = (sl - entry) * trading_pair['contract_size']
            pip_value_usd = pip_value_cross / self.get_usd_conversion_rate(symbol, is_backtesting)

        pip_value_usd = abs(pip_value_usd)

        # Calculate the risk amount in USD
        risk_amount_usd = (risk_percentage / 100) * account_balance

        # Calculate the lot size
        lots = risk_amount_usd / pip_value_usd

        return round(lots, 2)
