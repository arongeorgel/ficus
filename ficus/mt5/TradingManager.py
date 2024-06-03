from typing import List, TypedDict, Optional

from ficus.mt5.listeners.ITradingCallback import ITradingCallback


class FicusTrade(TypedDict):
    stop_loss_price: float
    entry_price: float
    position: int  # one of 1 (buy) or -1 (sell)
    take_profit: float
    position_id: int  # from meta_api
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


class TradingManager:
    current_trade: Optional[FicusTrade] = None
    __closed_trades: List[FicusTrade] = []

    def __init__(self, callback: ITradingCallback):
        self.callback: ITradingCallback = callback

    def _add_closed_trade(self, order: FicusTrade):
        self.__closed_trades.append(order)

    def close_current_trade(self):
        position_id = self.current_trade['position_id']
        self._add_closed_trade(self.current_trade)
        self.current_trade = None
        return position_id

    async def validate_price(self, price: float):
        if self.current_trade is not None:
            if self.current_trade['position'] == 1:  # Buy position
                if self.current_trade['stop_loss_price'] >= price:
                    print("Stop loss hit for buy position. Closing current trade.")
                    self.callback.close_trade()
                    # await self.__vantage.close_position()
                elif self.current_trade['take_profit'] <= price:
                    print("Take profit hit for buy position. Closing current trade.")
                    self.callback.close_trade()

            elif self.current_trade['position'] == -1:  # Sell position
                if self.current_trade['stop_loss_price'] <= price:
                    print("Stop loss hit for sell position. Closing current trade.")
                    self.callback.close_trade()
                elif self.current_trade['take_profit'] >= price:
                    print("Take profit hit for sell position. Closing current trade.")
                    self.callback.close_trade()

    def calculate_sl_and_tp(self, current_capital: float, symbol: str, direction):
        """
        For given symbol and given direction, calculate stop loss and take profit list
        stop_loss = entry_price - stop_loss_distance if signal == 1 else entry_price + stop_loss_distance
        take_profits = [(entry_price + tp * 0.1 if signal == 1 else entry_price - tp * 0.1, calculate_dollars(tp * 0.1, volume)) for tp in profit_pips]
        :return:
        """
