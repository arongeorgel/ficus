from typing import TypedDict, Optional

BOT_NUMBER_FRED_MAIN = 2341004
BOT_NUMBER_FRED_RISK = 2341005


class TradingSymbol:
    XAUUSD = 'XAUUSD'
    BTCUSD = 'BTCUSD'
    EURUSD = 'EURUSD'
    USDJPY = 'USDJPY'
    USDCHF = 'USDCHF'
    GBPUSD = 'GBPUSD'
    USDCAD = 'USDCAD'
    NZDUSD = 'NZDUSD'
    AUDUSD = 'AUDUSD'

    # 1 pip of gold = $0.01. $5 difference is 500 pips. on 500:1 account that is $500 minus broker fee
    #                        $1 difference is 100 pips
    #                        On volume 1, 100 pips difference is $100
    # 1 pip of eurusd = $0.00001. $1 difference is 500 000 pips.on 500:1 account that is 500 000 minus broker fee
    #                             $0.001 difference is 100 pips.
    #                             On volume 1, 100 pips difference is $100
    @staticmethod
    def calculate_levels(symbol: str, entry_price, direction, risk_level: int):
        """

        :param entry_price: price at which the trade was opened
        :param symbol: forex symbol
        :param direction: buy or sell
        :param risk_level: 0 - very high, 1- high, else - normal
        :return: stop_loss, take_profit1, take_profit2, take_profit3, volume
        """

        if risk_level == 0:
            risk_percent = 2 / 100
        elif risk_level == 1:
            risk_percent = 3 / 100
        else:
            risk_percent = 5 / 100
        max_risk = 4000 * risk_percent  # $80

        # Define differences for each symbol
        if symbol is TradingSymbol.XAUUSD:
            sl_difference = 3.0
            tp1_difference = 3.0
            tp2_difference = 5.0
            tp3_difference = 10.0
            tp4_difference = 15.0
            contract_size = 100.0
            price_precision = 2
        elif symbol is TradingSymbol.BTCUSD:
            sl_difference = 300
            tp1_difference = 300
            tp2_difference = 500
            tp3_difference = 1000
            tp4_difference = 2000
            contract_size = 1
            price_precision = 2
        elif symbol is TradingSymbol.EURUSD:
            sl_difference = 0.003
            tp1_difference = 0.003
            tp2_difference = 0.005
            tp3_difference = 0.01
            tp4_difference = 0.012
            contract_size = 100000
            price_precision = 5
        elif symbol is TradingSymbol.AUDUSD:
            sl_difference = 0.003
            tp1_difference = 0.003
            tp2_difference = 0.005
            tp3_difference = 0.01
            tp4_difference = 0.012
            contract_size = 100000
            price_precision = 5
        elif symbol is TradingSymbol.GBPUSD:
            sl_difference = 0.003
            tp1_difference = 0.003
            tp2_difference = 0.005
            tp3_difference = 0.01
            tp4_difference = 0.012
            contract_size = 100000
            price_precision = 5
        elif symbol is TradingSymbol.NZDUSD:
            sl_difference = 0.003
            tp1_difference = 0.003
            tp2_difference = 0.005
            tp3_difference = 0.01
            tp4_difference = 0.012
            contract_size = 100000
            price_precision = 5
        elif symbol is TradingSymbol.USDCAD:
            sl_difference = 0.003
            tp1_difference = 0.003
            tp2_difference = 0.005
            tp3_difference = 0.01
            tp4_difference = 0.012
            contract_size = 100000
            price_precision = 5
        elif symbol is TradingSymbol.USDCHF:
            sl_difference = 0.003
            tp1_difference = 0.003
            tp2_difference = 0.005
            tp3_difference = 0.01
            tp4_difference = 0.012
            contract_size = 100000
            price_precision = 5
        elif symbol is TradingSymbol.USDJPY:
            sl_difference = 0.5
            tp1_difference = 0.5
            tp2_difference = 1.5
            tp3_difference = 2
            tp4_difference = 4
            contract_size = 1000
            price_precision = 3
        else:
            raise ValueError("Unsupported symbol. Please use one of the values of TradingSymbol")

        # Calculate volume based on max_risk, sl_difference and contract size
        volume = round(max_risk / sl_difference / contract_size, 2)

        # Calculate stop loss and take profit levels
        if direction == TradeDirection.BUY:
            stop_loss = round(entry_price - sl_difference, price_precision)
            take_profit1 = round(entry_price + tp1_difference, price_precision)
            take_profit2 = round(entry_price + tp2_difference, price_precision)
            take_profit3 = round(entry_price + tp3_difference, price_precision)
            take_profit4 = round(entry_price + tp4_difference, price_precision)
        elif direction == TradeDirection.SELL:
            stop_loss = round(entry_price + sl_difference, price_precision)
            take_profit1 = round(entry_price - tp1_difference, price_precision)
            take_profit2 = round(entry_price - tp2_difference, price_precision)
            take_profit3 = round(entry_price - tp3_difference, price_precision)
            take_profit4 = round(entry_price - tp4_difference, price_precision)
        else:
            raise ValueError(f"Unsupported direction {direction}. Please use 'buy' or 'sell'.")

        return stop_loss, take_profit1, take_profit2, take_profit3, take_profit4, volume


def get_vantage_trading_symbol(symbol: str):
    if symbol == 'BTCUSD':
        return symbol
    else:
        return symbol + '+'


class TradeDirection:
    BUY = 1
    SELL = -1
    HOLD = 0


class FicusTrade(TypedDict):
    stop_loss_price: float
    entry_price: float
    trade_direction: str  # 'buy' or 'sell'
    take_profits: list[float]
    take_profits_hit: list[bool]
    start_volume: float
    volume: float
    position_id: Optional[str]  # from meta_api
    message_id: str
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
