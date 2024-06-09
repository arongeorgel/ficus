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

    # 1 pip of gold = $0.01. $5 difference is 500 pips. on 500:1 account that is $500 minus broker fee
    #                        $1 difference is 100 pips
    #                        On volume 1, 100 pips difference is $100
    # 1 pip of eurusd = $0.00001. $1 difference is 500 000 pips.on 500:1 account that is 500 000 minus broker fee
    #                             $0.001 difference is 100 pips.
    #                             On volume 1, 100 pips difference is $100
    def calculate_levels(self, entry_price, direction):
        """

        :param entry_price: price at which the trade was opened
        :param direction: buy or sell
        :return: stop_loss, take_profit1, take_profit2, take_profit3, volume
        """
        # Constants
        risk_percent = 2 / 100
        max_risk = 4000 * risk_percent  # $80

        # Define differences for each symbol
        if self is TradingSymbol.XAUUSD:
            sl_difference = 3
            tp1_difference = 3
            tp2_difference = 5
            tp3_difference = 10
            tp4_difference = 25
            contract_size = 100
            price_precision = 2
        elif self is TradingSymbol.BTCUSD:
            sl_difference = 300
            tp1_difference = 300
            tp2_difference = 500
            tp3_difference = 1000
            tp4_difference = 2500
            contract_size = 1
            price_precision = 2
        elif self is TradingSymbol.EURUSD:
            sl_difference = 0.004
            tp1_difference = 0.004
            tp2_difference = 0.007
            tp3_difference = 0.012
            tp4_difference = 0.02
            contract_size = 100000
            price_precision = 5
        else:
            raise ValueError("Unsupported symbol. Please use one of the values of TradingSymbol")

        # Calculate volume based on max_risk, sl_difference and contract size
        volume = round(max_risk / sl_difference / contract_size, 2)

        # Calculate stop loss and take profit levels
        if direction is TradeDirection.BUY:
            stop_loss = round(entry_price - sl_difference, price_precision)
            take_profit1 = round(entry_price + tp1_difference, price_precision)
            take_profit2 = round(entry_price + tp2_difference, price_precision)
            take_profit3 = round(entry_price + tp3_difference, price_precision)
        elif direction is TradeDirection.SELL:
            stop_loss = round(entry_price + sl_difference, price_precision)
            take_profit1 = round(entry_price - tp1_difference, price_precision)
            take_profit2 = round(entry_price - tp2_difference, price_precision)
            take_profit3 = round(entry_price - tp3_difference, price_precision)
        else:
            raise ValueError("Unsupported direction. Please use 'buy' or 'sell'.")

        return stop_loss, take_profit1, take_profit2, take_profit3, volume


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
    take_profits: tuple[float, float, float]
    take_profits_hit: list[bool]
    start_volume: float
    volume: float
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
