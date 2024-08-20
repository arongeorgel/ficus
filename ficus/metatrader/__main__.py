import asyncio

from ficus.metatrader.MetatraderTerminal import MetatraderTerminal
from ficus.metatrader.MemoryStorage import open_trades
from ficus.models.logger import ficus_logger
from ficus.models.models import FicusTrade, BOT_NUMBER_FRED_MAIN
from ficus.models.utils import find_trade_by_id
from ficus.signals.listen_for_new_messages import start_listening_telegra_messages, telethon_client


async def start_monitoring_trades():
    while True:
        # get all positions open
        try:
            open_positions = MetatraderTerminal.get_open_positions()

            if open_positions is not None or len(open_trades) > 0:
                # sync against what is in memory
                open_trades_copy = open_trades.copy()
                if open_positions is not None and open_trades is not None and len(open_positions) != len(open_trades_copy):
                    for position in open_positions:
                        if position.ticket not in open_trades_copy:
                            print(f'Removing {position.ticket} as it could not be found in memory')
                            logger.info(f'Removing {position.ticket} as it could not be found in memory')
                            del open_trades[position.ticket]

                # check for prices
                for position in open_positions:
                    memory_trade = find_trade_by_id(open_trades, position.ticket)
                    price = MetatraderTerminal.get_current_price(memory_trade['symbol'],
                                                                 memory_trade['trade_direction'])

                    await validate_price(price, memory_trade)
        except Exception:
            pass

        # check again after 5 seconds
        await asyncio.sleep(5)


def _modify_trade_sl(trade: FicusTrade):
    if trade['position_id'] is not None:
        open_trades[trade['position_id']] = trade


async def validate_price(price: float, trade: FicusTrade):
    direction = trade['trade_direction']
    volume = trade['start_volume']
    trading_symbol = trade['symbol']
    tolerance = 0.000001
    memory_trade = find_trade_by_id(open_trades, trade['position_id'])

    if direction == "buy":
        # TP3
        if price >= trade['take_profits'][2] + tolerance and not trade['take_profits_hit'][2]:
            ficus_logger.info(f"Take profit 3 hit for {trade['symbol']} on buy at price {price}")
            print(f"Take profit 3 hit for {trade['symbol']} on buy at price {price}")
            trade['take_profits_hit'][2] = True
            # await self._close_trade(trade, trading_symbol, "all TP hit on buy")
        # TP2
        elif price >= trade['take_profits'][1] + tolerance and not trade['take_profits_hit'][1]:
            ficus_logger.info(f"Take profit 2 hit for {trade['symbol']} on buy at price {price}")
            print(f"Take profit 2 hit for {trade['symbol']} on buy at price {price}")
            trade['volume'] = round(volume / 2, 2)
            trade['take_profits_hit'][1] = True
            MetatraderTerminal.close_trade(
                symbol=trading_symbol,
                trade_id=trade['position_id'],
                bot_number=BOT_NUMBER_FRED_MAIN,
                full_close=False
            )
            update_open_trades(trade)

            # modify the position
            if memory_trade is not None:
                trade['stop_loss_price'] = memory_trade['entry_price']
                _modify_trade_sl(trade)
        # TP 1
        elif price >= trade['take_profits'][0] + tolerance and not trade['take_profits_hit'][0]:
            ficus_logger.info(f"Take profit 1 hit for {trade['symbol']} on buy at price {price}")
            print(f"Take profit 1 hit for {trade['symbol']} on buy at price {price}")
            trade['take_profits_hit'][0] = True
            trade['volume'] = round(volume / 2, 2)
            MetatraderTerminal.close_trade(
                symbol=trading_symbol,
                trade_id=trade['position_id'],
                bot_number=BOT_NUMBER_FRED_MAIN,
                full_close=False
            )
            update_open_trades(trade)

    elif direction == 'sell':
        # TP 3
        if price <= trade['take_profits'][2] - tolerance and not trade['take_profits_hit'][2]:
            ficus_logger.info(f"Take profit 3 hit for {trade['symbol']} on sell at price {price}")
            print(f"Take profit 3 hit for {trade['symbol']} on sell at price {price}")
            trade['take_profits_hit'][2] = True
            # await self._close_trade(trade, trading_symbol, "all TP hit on sell")
        # TP 2
        elif price <= trade['take_profits'][1] - tolerance and not trade['take_profits_hit'][1]:
            ficus_logger.info(f"Take profit 2 hit for {trade['symbol']} on sell at price {price}")
            print(f"Take profit 2 hit for {trade['symbol']} on sell at price {price}")
            trade['volume'] = round(volume / 2, 2)
            trade['take_profits_hit'][1] = True
            MetatraderTerminal.close_trade(
                symbol=trading_symbol,
                trade_id=trade['position_id'],
                bot_number=BOT_NUMBER_FRED_MAIN,
                full_close=False
            )
            update_open_trades(trade)

            # modify the position
            if memory_trade is not None:
                trade['stop_loss_price'] = memory_trade['entry_price']
                _modify_trade_sl(trade)
        # TP 1
        elif price <= trade['take_profits'][0] - tolerance and not trade['take_profits_hit'][0]:
            ficus_logger.info(f"Take profit 1 hit for {trade['symbol']} on buy at price {price}")
            print(f"Take profit 1 hit for {trade['symbol']} on buy at price {price}")
            trade['take_profits_hit'][0] = True
            trade['volume'] = round(volume / 2, 2)
            MetatraderTerminal.close_trade(
                symbol=trading_symbol,
                trade_id=trade['position_id'],
                bot_number=BOT_NUMBER_FRED_MAIN,
                full_close=False
            )
            update_open_trades(trade)


def update_open_trades(trade):
    position_id = trade['position_id']
    if position_id is not None:
        open_trades[position_id] = trade


async def start_monitoring():
    while True:
        print("Monitoring...")
        try:
            open_positions = MetatraderTerminal.get_open_positions()
        except Exception as e:
            pass

        await asyncio.sleep(5)


async def main():
    task1 = asyncio.create_task(start_listening_telegra_messages())
    task2 = asyncio.create_task(start_monitoring_trades())
    await asyncio.gather(task1, task2)


if __name__ == "__main__":
    MetatraderTerminal.init_metatrader_terminal()
    with telethon_client:
        telethon_client.loop.run_until_complete(main())
