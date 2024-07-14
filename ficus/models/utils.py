from typing import Optional

from ficus.models.models import FicusTrade

trade: FicusTrade
find_trade_by_tmsg = lambda trades, message_id: (
    next((trade for trade in trades if trade['message_id'] == message_id), None))
