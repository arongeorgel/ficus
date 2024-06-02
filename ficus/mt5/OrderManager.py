from dataclasses import dataclass
from typing import List, TypedDict

from metaapi_cloud_sdk.metaapi.models import MetatraderTradeResponse


class OrderManager:
    order_list: List[MetatraderTradeResponse] = []

    def _add_order(self, order: MetatraderTradeResponse):
        self.order_list.append(order)

    def calculate_sl_and_tp(self, current_capital: float, symbol: str, direction):
        """
        For given symbol and given direction, calculate stop loss and take profit list
        stop_loss = entry_price - stop_loss_distance if signal == 1 else entry_price + stop_loss_distance
        take_profits = [(entry_price + tp * 0.1 if signal == 1 else entry_price - tp * 0.1, calculate_dollars(tp * 0.1, volume)) for tp in profit_pips]
        :return:
        """


@dataclass
class FicusTrade(TypedDict):
    stop_loss_price: float
    entry_price: float
    position: int  # one of 1 (buy) or -1 (sell)
    take_profits: List[float]
    order_id: int
    position_id: int
    symbol: str

    # {
    # 'numericCode': 10009,
    # 'stringCode': 'TRADE_RETCODE_DONE',
    # 'message': 'Request completed',
    # 'orderId': '87651455',
    # 'positionId': '87651455',
    # 'tradeExecutionTime': datetime.datetime(2024, 5, 31, 15, 13, 2, 253000, tzinfo=datetime.timezone.utc),
    # 'tradeStartTime': datetime.datetime(2024, 5, 31, 15, 13, 1, 721000, tzinfo=datetime.timezone.utc)
    # }
