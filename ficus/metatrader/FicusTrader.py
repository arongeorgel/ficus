import asyncio
import traceback

from ficus.metatrader.Terminal import Terminal
from ficus.metatrader.MemoryStorage import MemoryStorage
from ficus.models.logger import ficus_logger
from ficus.models.models import FicusTrade


# noinspection PyBroadException
class FicusTrader:
    __PRICE_TOLERANCE = 0.000001

    def __init__(self, terminal: Terminal, storage: MemoryStorage, bot_number):
        self.terminal = terminal
        self.storage = storage
        self.bot_number = bot_number

    async def monitor_active_trades(self):
        """
        Every 5 seconds the trader looks over at the terminal and will check how each running trade is doing.
        Based on configuration, it may update the stop loss, take some profits or take a hit and close a trade
        :return:
        """
        while True:
            try:
                open_positions = self.terminal.get_open_positions()
                for position in open_positions:
                    # 1. find the trade in memory
                    memory_trade = self.storage.get_trade(position.ticket)
                    # MAC Trade
                    # memory_trade = self.storage.get_trade(position['position_id'])
                    if memory_trade is None:
                        break
                    # 2. if not in memory, reconcile and ask the telegram bot to search for a message
                    # where entry and stop loss matches. This is complex as we can't look over all messages.
                    # 3. if the telegram bot returns nothing, send me a message and ask what to do
                    # 4. future implementation - look over last week ohlc and based on 1h trades take a self decision

                    price = self.terminal.get_current_price(memory_trade['symbol'], memory_trade['trade_direction'])
                    if memory_trade['trade_direction'] == 'buy':
                        self._validate_price_on_buy(price, memory_trade)
                    elif memory_trade['trade_direction'] == 'sell':
                        self._validate_price_on_sell(price, memory_trade)
            except Exception:
                message = f'Failed to get open positions at this time. {traceback.format_exc()}'
                ficus_logger.error(message)
                print(message)
                pass
            await asyncio.sleep(5)

    def _validate_price_on_buy(self, price, trade: FicusTrade):
        # Stop loss
        if price < trade['stop_loss_price']:
            self.terminal.close_trade(trade['symbol'],
                                      trade['position_id'],
                                      trade['volume'],
                                      self.bot_number,
                                      True)
            self.storage.sync_terminal()
        # TP3
        if price >= trade['take_profits'][2] + self.__PRICE_TOLERANCE and not trade['take_profits_hit'][2]:
            ficus_logger.info(f"Take profit 3 hit for {trade['symbol']} on buy at price {price}")
            print(f"Take profit 3 hit for {trade['symbol']} on buy at price {price}")

            self.storage.sync_terminal()
        # TP2
        elif price >= trade['take_profits'][1] + self.__PRICE_TOLERANCE and not trade['take_profits_hit'][1]:
            ficus_logger.info(f"Take profit 2 hit for {trade['symbol']} on buy at price {price}")
            print(f"Take profit 2 hit for {trade['symbol']} on buy at price {price}")

            self.__action(trade, True, 1)
        # TP 1
        elif price >= trade['take_profits'][0] + self.__PRICE_TOLERANCE and not trade['take_profits_hit'][0]:
            ficus_logger.info(f"Take profit 1 hit for {trade['symbol']} on buy at price {price}")
            print(f"Take profit 1 hit for {trade['symbol']} on buy at price {price}")

            self.__action(trade, True, 0)

    def _validate_price_on_sell(self, price, trade: FicusTrade):
        # Stop loss
        if price > trade['stop_loss_price']:
            self.terminal.close_trade(trade['symbol'],
                                      trade['position_id'],
                                      trade['volume'],
                                      self.bot_number,
                                      True)
            self.storage.sync_terminal()
        # TP 3
        if price <= trade['take_profits'][2] - self.__PRICE_TOLERANCE and not trade['take_profits_hit'][2]:
            ficus_logger.info(f"Take profit 3 hit for {trade['symbol']} on sell at price {price}")
            print(f"Take profit 3 hit for {trade['symbol']} on sell at price {price}")

            self.storage.sync_terminal()
        # TP 2
        elif price <= trade['take_profits'][1] - self.__PRICE_TOLERANCE and not trade['take_profits_hit'][1]:
            ficus_logger.info(f"Take profit 2 hit for {trade['symbol']} on sell at price {price}")
            print(f"Take profit 2 hit for {trade['symbol']} on sell at price {price}")

            self.__action(trade, True, 1)
        # TP 1
        elif price <= trade['take_profits'][0] - self.__PRICE_TOLERANCE and not trade['take_profits_hit'][0]:
            ficus_logger.info(f"Take profit 1 hit for {trade['symbol']} on buy at price {price}")
            print(f"Take profit 1 hit for {trade['symbol']} on buy at price {price}")

            self.__action(trade, False, 0)

    def __action(self, trade: FicusTrade, update_sl: bool, profit_nr: int):
        volume = round(trade['start_volume'] / 2, 2)
        validated_volume = trade['start_volume'] if volume == 0 else volume
        trade['volume'] = validated_volume
        trade['take_profits_hit'][profit_nr] = True

        self.terminal.close_trade(
            symbol=trade['symbol'],
            trade_id=trade['position_id'],
            bot_number=self.bot_number,
            volume=validated_volume,
            full_close=False)

        if update_sl:
            self.terminal.update_stop_loss(trade['symbol'], trade['position_id'])

        self.storage.update_trade(trade)
