import logging

import MetaTrader5 as mt5

from ficus.models.models import FicusTrade, BOT_NUMBER_FRED_MAIN


class MetatraderTerminal:

    @staticmethod
    def execute_pending_trade(trade: FicusTrade, bot_number):
        symbol = trade['symbol']
        action = mt5.ORDER_TYPE_BUY if trade['trade_direction'] == 'buy' else mt5.ORDER_TYPE_SELL
        volume = trade['volume']
        price = trade['entry_price']
        sl = trade['stop_loss_price']
        tps = trade['take_profits']

        tp = max(tps) if action == mt5.ORDER_TYPE_BUY else min(tps)

        request = {
            'action': mt5.TRADE_ACTION_PENDING,
            'symbol': symbol,
            'volume': volume,
            'type': action,
            'price': price,
            'sl': sl,
            'tp': tp,
            'deviation': 20,
            'magic': BOT_NUMBER_FRED_MAIN,
            'comment': 'Python script order',
            'type_time': mt5.ORDER_TIME_GTC,
            'type_filling': mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logging.error("Order failed, retcode=%s", result.retcode)
        else:
            logging.info("Order placed, trade_id=%s", result.order)
            return result.order


    @staticmethod
    def close_trade(symbol, trade_id, full_close=False):
        positions = mt5.positions_get(symbol=symbol)
        if not positions:
            logging.error("No open positions found for symbol: %s", symbol)
            return

        trade_to_close = next(t for t in positions if t.order == trade_id)
        action = mt5.ORDER_TYPE_SELL if trade_to_close.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        volume = trade_to_close.volume if full_close else trade_to_close.volume / 2

        request = {
            'action': mt5.TRADE_ACTION_DEAL,
            'symbol': symbol,
            'volume': volume,
            'type': action,
            'position': trade_to_close.ticket,
            'deviation': 20,
            'magic': BOT_NUMBER_FRED_MAIN,
            'comment': 'Python script close' if full_close else 'Python script partial close',
            'type_time': mt5.ORDER_TIME_GTC,
            'type_filling': mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logging.error("Close order failed, retcode=%s", result.retcode)
        else:
            logging.info("Trade %s closed, position_id=%s", "fully" if full_close else "partially", trade_to_close.ticket)


    @staticmethod
    def set_sl_to_entry(symbol, trade_id):
        positions = mt5.positions_get(symbol=symbol)
        if not positions:
            logging.error("No open positions found for symbol: %s", symbol)
            return

        trade_to_update = next(t for t in positions if t.ticket == trade_id)

        modify_request = {
            'action': mt5.TRADE_ACTION_SLTP,
            'position': trade_to_update.ticket,
            'sl': trade_to_update.price_open,
        }

        result = mt5.order_send(modify_request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logging.error("Modify SL to entry failed, retcode=%s", result.retcode)
        else:
            logging.info("SL set to entry price for position_id=%s", trade_to_update.ticket)
