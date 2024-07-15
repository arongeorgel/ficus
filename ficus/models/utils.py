from typing import Optional

from ficus.models.models import FicusTrade

def find_trade_by_tmsg(trades, message_id):
    print(f'trades: {trades}\n msgId={message_id}')
    for trade in trades.values():
        if trade['message_id'] == message_id:
            return trade
    return None

