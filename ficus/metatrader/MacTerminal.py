import random

from ficus.metatrader.Terminal import Terminal
from ficus.models.models import FicusTrade


class MacTerminal(Terminal):
    trades: dict[str, FicusTrade] = {}
    price_history: dict[str, float] = {
    }
    fluctuation_range = 0.25
    market_entry: dict[str, float] = {
        # 'XAUUSD': {'min_value': 2000.00, 'max_value': 2010.00},
        # You can add more currency pairs here with their respective min/max ranges
    }

    def init(self):
        print("Mac terminal initialised!")

    def open_trade(self, trade: FicusTrade, bot_number):
        trade_id = "test-" + str(random.randint(1000, 9999))

        trade['position_id'] = trade_id
        self.trades[trade_id] = trade
        self.market_entry[trade['symbol']] = trade['entry_price']
        self.price_history[trade['symbol']] = trade['entry_price']

        return trade_id

    def update_stop_loss(self, symbol, trade_id):
        print(f"Updated SL to entry")

    def get_open_positions(self):
        return self.trades.values()

    def get_current_price(self, symbol, direction):

        # Calculate the next value within a small range of the last value
        next_value = self.price_history[symbol] + random.uniform(-self.fluctuation_range, self.fluctuation_range)

        # Ensure the value stays within the specified range
        # next_value = max(min_value, min(next_value, max_value))

        # Update the global variable
        self.price_history[symbol] = next_value

        return next_value

    def determine_order_type(self, current_price, entry_price, order_direction):
        return ""

    def close_trade(self, symbol, trade_id, volume, bot_number, full_close):
        fully = "fully" if full_close is True else ""
        if full_close:
            del self.trades[trade_id]
            del self.market_entry[symbol]
            del self.price_history[symbol]
        print(f"Closed trade {trade_id} {fully}")
