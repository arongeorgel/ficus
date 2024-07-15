import logging

import MetaTrader5 as mt5

from ficus.models.models import FicusTrade

logger = logging.getLogger('ficus_logger')


class MetatraderTerminal:

    @staticmethod
    def init_metatrader_terminal():
        if not mt5.initialize():
            print("Failed to initialize MetaTrader5")
            mt5.shutdown()

    @staticmethod
    def get_open_positions():
        return mt5.positions_get()

    @staticmethod
    def get_current_price(symbol, direction):
        tick = mt5.symbol_info_tick(symbol)
        return tick['bid'] if direction == 'buy' else tick['ask']

    @staticmethod
    def determine_mt5_order_type(current_price, entry_price, order_direction):
        """
        Determine the MT5 order type based on the current price, entry price, and order direction.

        :param current_price: float, the current market price
        :param entry_price: float, the desired entry price
        :param order_direction: str, the direction of the order ('buy' or 'sell')
        :return: the MT5 order type
        """
        if order_direction.lower() == 'buy':
            if entry_price > current_price:
                return mt5.ORDER_TYPE_BUY_STOP
            elif entry_price < current_price:
                return mt5.ORDER_TYPE_BUY_LIMIT
        elif order_direction.lower() == 'sell':
            if entry_price > current_price:
                return mt5.ORDER_TYPE_SELL_STOP
            elif entry_price < current_price:
                return mt5.ORDER_TYPE_SELL_STOP
        else:
            logger.error(f"Invalid direction {order_direction}")
            return None
        #
        # # Example usage
        # current_price = 1.1000
        # entry_price = 1.1050
        # order_direction = 'buy'
        # print(determine_mt5_order_type(current_price, entry_price, order_direction))  # Output: 'buy stop'
        #

    @staticmethod
    def execute_pending_trade(trade: FicusTrade, bot_number):
        symbol = trade['symbol']
        price = trade['entry_price']
        volume = trade['volume']
        sl = trade['stop_loss_price']
        tps = trade['take_profits']
        direction = trade['trade_direction']

        current_price = MetatraderTerminal.get_current_price(symbol, direction)
        action = MetatraderTerminal.determine_mt5_order_type(current_price, price, direction)

        # tp = tps[2] max(tps) if action == mt5.ORDER_TYPE_BUY else min(tps)
        tp = tps[2]

        request = {
            'action': mt5.TRADE_ACTION_PENDING,
            'symbol': symbol,
            'volume': volume,
            'deviation': 20,
            'magic': bot_number,
            'type': action,
            'price': price,
            'stoplimit': price,
            'sl': sl,
            'tp': tp,
            'comment': 'Python script order'
        }

        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error("Open order failed, retcode=%s", result.retcode)
            result_dict = result._asdict()
            for field in result_dict.keys():
                print("   {}={}".format(field, result_dict[field]))
                # if this is a trading request structure, display it element by element as well
                if field == "request":
                    traderequest_dict = result_dict[field]._asdict()
                    for tradereq_filed in traderequest_dict:
                        print("       traderequest: {}={}".format(tradereq_filed, traderequest_dict[tradereq_filed]))
            return None
        else:
            logger.info("Order placed, trade_id=%s", result.order)
            return result.order

    @staticmethod
    def close_trade(symbol, trade_id, bot_number, full_close=False):
        positions = mt5.positions_get(ticket=trade_id)
        if not positions:
            logger.error("No open positions found for symbol: %s", symbol)
            return

        trade_to_close = positions[0]
        action = mt5.ORDER_TYPE_SELL if trade_to_close.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        volume = trade_to_close.volume if full_close else trade_to_close.volume / 2

        request = {
            'action': mt5.TRADE_ACTION_DEAL,
            'symbol': symbol,
            'volume': volume,
            'type': action,
            'position': trade_to_close.ticket,
            'deviation': 20,
            'magic': bot_number,
            'comment': 'Python script close' if full_close else 'Python script partial close',
            'type_time': mt5.ORDER_TIME_GTC,
            'type_filling': mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error("Closing order failed, retcode=%s", result.retcode)
            # request the result as a dictionary and display it element by element
            result_dict = result._asdict()
            for field in result_dict.keys():
                print("   {}={}".format(field, result_dict[field]))
                # if this is a trading request structure, display it element by element as well
                if field == "request":
                    traderequest_dict = result_dict[field]._asdict()
                    for tradereq_filed in traderequest_dict:
                        print("       traderequest: {}={}".format(tradereq_filed, traderequest_dict[tradereq_filed]))
        else:
            logger.info("Trade %s closed, position_id=%s", "fully" if full_close else "partially",
                        trade_to_close.ticket)

    @staticmethod
    def set_sl_to_entry(symbol, trade_id):
        positions = mt5.positions_get(ticket=trade_id)
        if not positions:
            logger.error("No open positions found for symbol: %s", symbol)
            return

        trade_to_update = positions[0]

        modify_request = {
            'action': mt5.TRADE_ACTION_SLTP,
            'position': trade_to_update.ticket,
            'sl': trade_to_update.price_open,
        }

        result = mt5.order_send(modify_request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error("Modify SL to entry failed, retcode=%s", result.retcode)
        else:
            logger.info("SL set to entry price for position_id=%s", trade_to_update.ticket)
