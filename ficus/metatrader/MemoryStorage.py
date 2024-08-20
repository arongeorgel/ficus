from typing import Optional

from ficus.models.models import FicusTrade


class MemoryStorage:

    __open_trades: dict[str, FicusTrade] = {}

    def add_trade(self, trade: FicusTrade) -> None:
        position_id = trade['position_id']
        if position_id is not None:
            self.__open_trades[position_id] = trade

    def remove_trade(self, trade_id: str) -> None:
        del self.__open_trades[trade_id]

    def get_trade(self, trade_id: str) -> FicusTrade:
        return self.__open_trades[trade_id]

    def get_trade_by_message_id(self, message_id: str) -> Optional[FicusTrade]:
        for trade in self.__open_trades.values():
            if trade['message_id'] == message_id:
                return trade

        return None

    def get_all_trades(self) -> list[FicusTrade]:
        return list(self.__open_trades.values())

    def sync_terminal(self):
        pass

    def update_trade(self, trade):
        if trade['position_id'] in self.__open_trades:
            self.__open_trades[trade['position_id']] = trade
