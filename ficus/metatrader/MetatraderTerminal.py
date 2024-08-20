import MetaTrader5 as mt5

from ficus.metatrader.Terminal import Terminal
from ficus.models.logger import ficus_logger
from ficus.models.models import FicusTrade, get_vantage_trading_symbol


# noinspection PyUnresolvedReferences
class MetatraderTerminal(Terminal):

    def init(self):
        if not mt5.initialize():
            print("Failed to initialize MetaTrader5")
            mt5.shutdown()
        else:
            print("Terminal is running")

    def open_trade(self, trade: FicusTrade, bot_number):
        price = trade['entry_price']
        volume = trade['volume']
        sl = trade['stop_loss_price']
        tps = trade['take_profits']
        direction = trade['trade_direction']
        symbol = trade['symbol']

        if not mt5.symbol_select(symbol):
            ficus_logger.error(f"Failed to select symbol {symbol}")
            print(f"Failed to select symbol {symbol}")
            return

        current_price = self.get_current_price(symbol, direction)
        action_type = self.determine_order_type(
            current_price,
            price,
            direction)
        nb_decimal = str(price)[::-1].find(".")

        tp = max(tps) if direction == 'buy' else min(tps)

        request = {
            'action': mt5.TRADE_ACTION_PENDING,
            'symbol': symbol,
            'volume': volume,
            'deviation': 20,
            'magic': bot_number,
            'type': action_type,
            'price': round(price, nb_decimal),
            'sl': round(sl, nb_decimal),
            'tp': round(tp, nb_decimal),
            'comment': 'Ficus order',
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        ficus_logger.info(f'Sending order request: {request}')
        print(f'Sending order request: {request}')

        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            ficus_logger.info(f"Failed to place initial order. Trying again with immediate execution. \n {result}")
            print(f"Failed to place initial order. Trying again with immediate execution. \n {result}")
            self.print_order_fail(result)

            request = {
                'action': mt5.TRADE_ACTION_DEAL,
                'symbol': symbol,
                'volume': volume,
                'deviation': 20,
                'magic': bot_number,
                'type': mt5.ORDER_TYPE_BUY if direction == 'buy' else mt5.ORDER_TYPE_SELL,
                'sl': round(sl, nb_decimal),
                'tp': round(tp, nb_decimal),
                'comment': 'Ficus order',
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            ficus_logger.info(f'Sending follow-up order request {request}')
            print(f'Sending follow-up order request {request}')

            result = mt5.order_send(request)
            if result is not None and result.retcode != mt5.TRADE_RETCODE_DONE:
                ficus_logger.info(f'Failed to place follow-up order. {result}')
                print(f'Failed to place follow-up order. {result}')
                self.print_order_fail(result)
                return None
            else:
                ficus_logger.info("Order placed (follow-up), trade_id=%s", result.order)
                print("Order placed (follow-up), trade_id=%s", result.order)
                return result.order
        else:
            ficus_logger.info("Order placed, trade_id=%s", result.order)
            print("Order placed (follow-up), trade_id=%s", result.order)
            return result.order

    # noinspection PyMethodMayBeStatic,PyProtectedMember
    def print_order_fail(self, result):
        ficus_logger.error("Open order failed, retcode=%s", result.retcode)
        print("Open order failed, retcode=%s", result.retcode)
        result_dict = result._asdict()
        for field in result_dict.keys():
            print("   {}={}".format(field, result_dict[field]))
            # if this is a trading request structure, display it element by element as well
            if field == "request":
                trade_request_dict = result_dict[field]._asdict()
                for tradereq_filed in trade_request_dict:
                    print("       trade_request: {}={}".format(tradereq_filed, trade_request_dict[tradereq_filed]))

    def update_stop_loss(self, symbol, trade_id):
        positions = mt5.positions_get(ticket=trade_id)
        if not positions:
            ficus_logger.error(f"No open positions found for symbol: {symbol}")
            return

        trade_to_update = positions[0]

        modify_request = {
            'action': mt5.TRADE_ACTION_SLTP,
            'position': trade_id,
            'sl': trade_to_update.price_open,
        }

        result = mt5.order_send(modify_request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Modify SL to entry failed, retcode={result.retcode}", result.retcode)
            print(result)
        else:
            print(f"SL set to entry price for position_id={trade_to_update.ticket}")

    def determine_order_type(self, current_price, entry_price, order_direction):
        print(f'{current_price}, {entry_price}, {order_direction}')
        if order_direction.lower() == 'buy':
            if entry_price > current_price:
                return mt5.ORDER_TYPE_BUY_STOP
            elif entry_price < current_price:
                return mt5.ORDER_TYPE_BUY_LIMIT
            else:
                return mt5.ORDER_TYPE_BUY
        elif order_direction.lower() == 'sell':
            if entry_price > current_price:
                return mt5.ORDER_TYPE_SELL_LIMIT
            elif entry_price < current_price:
                return mt5.ORDER_TYPE_SELL_STOP
            else:
                return mt5.ORDER_TYPE_SELL
        else:
            ficus_logger.error(f"Invalid direction {order_direction}")
            return None

    def get_open_positions(self):
        return mt5.positions_get()

    def get_current_price(self, symbol, direction):
        if mt5.symbol_select(symbol):
            tick = mt5.symbol_info_tick(symbol)._asdict()
            return tick['bid'] if direction == 'buy' else tick['ask']
        else:
            print(f"Failed to select {symbol} for fetching the price.")
            ficus_logger.error(f"Failed to select {symbol} for fetching the price.")

    def close_trade(self, symbol, trade_id, volume, bot_number, full_close):
        positions = mt5.positions_get(ticket=trade_id)
        if not positions:
            ficus_logger.error(f"No open positions found for symbol: {symbol} with ticket {trade_id}")
            print(f"No open positions found for symbol: {symbol} with ticket {trade_id}")
            return

        trade_to_close = positions[0]
        volume = trade_to_close.volume if full_close else round(trade_to_close.volume / 2, 2)
        symbol = get_vantage_trading_symbol(symbol)

        request = {
            'action': mt5.TRADE_ACTION_DEAL,
            'symbol': symbol,
            'volume': volume if volume > 0 else trade_to_close.volume,
            'type': mt5.ORDER_TYPE_SELL if trade_to_close.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
            'position': trade_id,
            'deviation': 20,
            'magic': bot_number,
            'comment': 'Ficus closing trade' if full_close else 'Ficus partially closing',
            'type_time': mt5.ORDER_TIME_GTC,
            'type_filling': mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            # ficus_logger.error(f"Closing order failed retcode={result.retcode}")
            print(f"Closing order failed retcode={result.retcode}")
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
            close_type = "fully" if full_close else "partially"
            # ficus_logger.info(f"Trade {close_type} closed, position_id={trade_id}")
            print(f"Trade {close_type} closed, position_id={trade_id}")
