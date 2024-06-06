from enum import Enum
from typing import TypedDict


class TradingSymbol(Enum):
    XAUUSD = 'XAUUSD'
    BTCUSD = 'BTCUSD'
    EURUSD = 'EURUSD'

    @staticmethod
    def from_value(name: str):
        for member in TradingSymbol:
            if member.name == name:
                return member

    @staticmethod
    def calculate_stop_loss_price(symbol, entry_price, direction):
        if symbol is TradingSymbol.XAUUSD:
            return entry_price + 5 if direction is TradeDirection.SELL else entry_price - 5
        elif symbol is TradingSymbol.BTCUSD:
            return entry_price + 100 if direction is TradeDirection.SELL else entry_price - 100
        elif symbol is TradingSymbol.EURUSD:
            return entry_price + 2 if direction is TradeDirection.SELL else entry_price - 2

    @staticmethod
    def calculate_take_profit(symbol, entry_price, direction):
        if symbol is TradingSymbol.XAUUSD:
            return entry_price - 5 if direction is TradeDirection.SELL else entry_price + 5
        elif symbol is TradingSymbol.BTCUSD:
            return entry_price - 100 if direction is TradeDirection.SELL else entry_price + 100
        elif symbol is TradingSymbol.EURUSD:
            return entry_price - 2 if direction is TradeDirection.SELL else entry_price + 2


class TradeDirection(Enum):
    BUY = 1
    SELL = -1
    HOLD = 0

    @staticmethod
    def from_value(value):
        for member in TradeDirection:
            if member.value == value:
                return member


class FicusTrade(TypedDict):
    stop_loss_price: float
    entry_price: float
    position: TradeDirection
    take_profit: float
    position_id: str  # from meta_api
    symbol: TradingSymbol

    # {
    # 'numericCode': 10009,
    # 'stringCode': 'TRADE_RETCODE_DONE',
    # 'message': 'Request completed',
    # 'orderId': '87651455',
    # 'positionId': '87651455',
    # 'tradeExecutionTime': datetime.datetime(2024, 5, 31, 15, 13, 2, 253000, tzinfo=datetime.timezone.utc),
    # 'tradeStartTime': datetime.datetime(2024, 5, 31, 15, 13, 1, 721000, tzinfo=datetime.timezone.utc)
    # }
