from typing import Optional

from ficus.models.models import FicusTrade


def find_trade_by_tmsg(trades, message_id):
    for trade in trades.values():
        if trade['message_id'] == message_id:
            return trade
    return None


def find_trade_by_prices(trades, entry, stop_loss, profits):
    """
    With given entry, stop loss and profit levels, find the trade. Convenient to use when the trade is not
    in memory, but still running in the terminal.
    :param trades:
    :param entry:
    :param stop_loss:
    :param profits
    :return:
    """
    return None


def find_trade_by_id(trades, trade_id) -> Optional[FicusTrade]:
    return next(trade for trade in trades.values() if trade_id == trade['position_id'])
