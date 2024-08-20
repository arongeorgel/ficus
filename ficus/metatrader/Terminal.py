from abc import ABC, abstractmethod

from ficus.models.models import FicusTrade


class Terminal(ABC):
    @abstractmethod
    def init(self):
        pass

    @abstractmethod
    def open_trade(self, trade: FicusTrade, bot_number):
        pass

    @abstractmethod
    def update_stop_loss(self, symbol, trade_id):
        """
        Update stop loss of given trade to entry or to given price if not None
        :param symbol:
        :param trade_id:
        :return:
        """
        pass

    @abstractmethod
    def get_open_positions(self):
        pass

    @abstractmethod
    def get_current_price(self, symbol, direction):
        pass

    @abstractmethod
    def determine_order_type(self, current_price, entry_price, order_direction):
        """
        Determine the MT5 order type based on the current price, entry price, and order direction.

        :param current_price: float, the current market price
        :param entry_price: float, the desired entry price
        :param order_direction: str, the direction of the order ('buy' or 'sell')
        :return: the MT5 order type
        """
        pass

    @abstractmethod
    def close_trade(self, symbol, trade_id, volume, bot_number, full_close):
        pass
