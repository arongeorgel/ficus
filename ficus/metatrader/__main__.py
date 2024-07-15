import asyncio
import logging

from ficus.metatrader.metatrader_terminal import MetatraderTerminal
from ficus.metatrader.trades_storage import open_trades
from ficus.models.models import FicusTrade, BOT_NUMBER_FRED_MAIN
from ficus.signals.telegram_messages import start_telegram_bot

logger = logging.getLogger('ficus_logger')


async def start_monitoring_trades():
    while True:
        # get all positions open
        open_positions = MetatraderTerminal.get_open_positions()

        if open_positions is None:
            return

        # quick check against what is in memory
        # if open_positions is not None and open_trades is not None and len(open_positions) != len(open_trades.copy()):
        #   logger.error("There is a discrepancy between memory and terminal in trades.")

        # check for prices
        for position in open_positions:
            memory_trade = next(trade for trade in open_trades.values() if position.ticket == trade['position_id'])
            price = MetatraderTerminal.get_current_price(position['symbol'], memory_trade['trade_direction'])

            await validate_price(price, memory_trade)

        # check again after 5 seconds
        await asyncio.sleep(5)


async def validate_price(price: float, trade: FicusTrade):
    direction = trade['trade_direction']
    volume = trade['start_volume']
    trading_symbol = trade['symbol']

    if direction == "buy":
        # SL
        # if price <= trade['stop_loss_price']:
        #     logger.info(f"Stop loss hit for {trade['symbol']} on buy at price {price}")
        #     MetatraderTerminal.close_trade()
        #     await self._close_trade(trade, trading_symbol, "stop loss hit on buy")
        # TP3
        if price >= trade['take_profits'][2] and not trade['take_profits_hit'][2]:
            logger.info(f"Take profit 3 hit for {trade['symbol']} on buy at price {price}")
            trade['take_profits_hit'][2] = True
            # await self._close_trade(trade, trading_symbol, "all TP hit on buy")
        # TP2
        elif price >= trade['take_profits'][1] and not trade['take_profits_hit'][1]:
            logger.info(f"Take profit 2 hit for {trade['symbol']} on buy at price {price}")
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
            # trade['stop_loss_price'] = entry_price
            # await self._modify_trade(trade)
        # TP 1
        elif price >= trade['take_profits'][0] and not trade['take_profits_hit'][0]:
            logger.info(f"Take profit 1 hit for {trade['symbol']} on buy at price {price}")
            trade['take_profits_hit'][0] = True
            trade['volume'] = round(volume / 2, 2)
            MetatraderTerminal.close_trade(
                symbol=trading_symbol,
                trade_id=trade['position_id'],
                bot_number=BOT_NUMBER_FRED_MAIN,
                full_close=False
            )
            update_open_trades(trade)
            # await self._partially_close_trade(trade, trading_symbol)

            # modify the position, update stop loss
            # trade['stop_loss_price'] = entry_price - ((entry_price - trade['stop_loss_price']) / 2)
            # await self._modify_trade(trade)

    elif direction == 'sell':
        # SL
        # if price >= trade['stop_loss_price']:
        #     logger.info(f"Stop loss hit for {trade['symbol']} on sell at price {price}")
        #     await self._close_trade(trade, trading_symbol, "stop loss hit on sell")
        # TP 3
        if price <= trade['take_profits'][2] and not trade['take_profits_hit'][2]:
            logger.info(f"Take profit 3 hit for {trade['symbol']} on sell at price {price}")
            trade['take_profits_hit'][2] = True
            # await self._close_trade(trade, trading_symbol, "all TP hit on sell")
        # TP 2
        elif price <= trade['take_profits'][1] and not trade['take_profits_hit'][1]:
            logger.info(f"Take profit 2 hit for {trade['symbol']} on sell at price {price}")
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
            # trade['stop_loss_price'] = entry_price
            # await self._modify_trade(trade)
        # TP 1
        elif price <= trade['take_profits'][0] and not trade['take_profits_hit'][0]:
            logger.info(f"Take profit 1 hit for {trade['symbol']} on buy at price {price}")
            trade['take_profits_hit'][0] = True
            trade['volume'] = round(volume / 2, 2)
            MetatraderTerminal.close_trade(
                symbol=trading_symbol,
                trade_id=trade['position_id'],
                bot_number=BOT_NUMBER_FRED_MAIN,
                full_close=False
            )
            update_open_trades(trade)

            # modify the position, update stop loss
            # trade['stop_loss_price'] = entry_price + ((entry_price - trade['stop_loss_price']) / 2)
            # await self._modify_trade(trade)


def update_open_trades(trade):
    position_id = trade['position_id']
    if position_id is not None:
        open_trades[position_id] = trade


async def main():
    # create task for signals
    telegram_task = asyncio.create_task(start_telegram_bot())
    # create task for terminal monitoring
    terminal_task = asyncio.create_task(start_monitoring_trades())

    await asyncio.gather(telegram_task, terminal_task)

    # Keep the main coroutine running
    while True:
        await asyncio.sleep(1)


if __name__ == '__main__':
    MetatraderTerminal.init_metatrader_terminal()
    asyncio.run(main())
