import datetime
import traceback

import yfinance as yf
from telethon import TelegramClient, events

from ficus.metatrader.MemoryStorage import MemoryStorage
from ficus.metatrader.Terminal import Terminal
from ficus.models.logger import ficus_logger
from ficus.signals.message_parser import extract_trade_symbol, should_close_trade_fully, is_sl_update, \
    parse_trade_message


# noinspection PyBroadException
class TelegramBot:
    __TELEGRAM_TOKEN = '7495868354:AAG8j_HS-wGmXz7Dr9Y-5As6hOkBGEXEYSs'
    __FRED_MAIN = -1001239815745
    __MYSELF = 6023501559
    __FICUS = 1234

    __API_ID = 21257186
    __API_HASH = '71bf8d6d969e25ddba66fdc1fd0c50c6'
    __PHONE_NUMBER = '+31610833394'

    def __init__(self, terminal: Terminal, storage: MemoryStorage, bot_number):
        self.client = TelegramClient('ficus-trader', self.__API_ID, self.__API_HASH)
        self.terminal = terminal
        self.storage = storage
        self.bot_number = bot_number

        # Register the event handler
        self.client.on(events.NewMessage)(self.handler)

    async def handler(self, event):
        chat = await event.get_chat()
        if chat.id == 1622898322 or chat.id == 1465548315:
            return

        print(f'==========         [START - {datetime.datetime.now().strftime("%A %H:%M")}]         =========')
        try:
            message = event.message
            if hasattr(message, 'is_reply') and message.is_reply:
                original_message = await message.get_reply_message()
                self.handle_reply_message(message.raw_text, original_message.raw_text, original_message.id)
            else:
                self.handle_message(message.raw_text, message.id)

        except Exception:
            print('----  traceback  ----')
            print(traceback.format_exc())
            print('---------------------')

        print("==========             [END]             ==========\n")

    def handle_message(self, message_text, message_id):
        trade = parse_trade_message(message_text, message_id, self.get_usd_conversion_rate)
        if trade is not None:
            ficus_logger.info(f"Parsed trade {trade}")
            print(f"Parsed trade {trade}")

            position_id = self.terminal.open_trade(trade, self.bot_number)
            # error handling happens further in open_trade, not need to add an else here.
            if position_id is not None:
                trade['position_id'] = position_id
                self.storage.add_trade(trade)
        else:
            ficus_logger.warning(f"Failed to parse trade.")
            print(f"Failed to parse trade.")

    def get_usd_conversion_rate(self, symbol, trade_direction, is_backtesting: bool = True):
        # sometimes the pair is <symbol[3:]>+USD
        pair = 'USD' + symbol[3:]
        reversed_pair = symbol[3:] + 'USD'
        if is_backtesting:
            return yf.download(pair + "=X", period='1d')['Close'].iloc[-1]
        else:
            usd_rate = self.terminal.get_current_price(pair, trade_direction)
            # if usd_rate is none, reverse the pair
            if usd_rate is None:
                usd_rate = self.terminal.get_current_price(reversed_pair, trade_direction)
                print(f'USD rate for {reversed_pair} is {1/usd_rate}')
                ficus_logger.info(f'USD rate for {reversed_pair} is {1/usd_rate}')

                # invert the rate
                return 1 / usd_rate
            else:
                print(f'USD rate for {pair} is {usd_rate}')
                ficus_logger.info(f'USD rate for {pair} is {usd_rate}')
                return usd_rate

    def handle_reply_message(self, text, original_message_text, original_message_id):
        """
        Reply messages are usually used for informing to close at profit or at lose.
        Sometimes they are used to update a given trade, this is a TODO
        :param text:
        :param original_message_text:
        :param original_message_id:
        :return:
        """
        # search for the symbol in the original message:
        symbol = extract_trade_symbol(original_message_text, original_message_id)

        if symbol is not None:
            trade = self.storage.get_trade_by_message_id(original_message_id)
            if trade is None:
                ficus_logger.warning(f"Could not find in memory an open trade for reply on {symbol}")
                print(f"Could not find in memory an open trade for reply on {symbol}")
            else:
                if should_close_trade_fully(text):
                    ficus_logger.info(f"Closing trade fully for {symbol}")
                    print(f"Closing trade fully for {symbol}")
                    self.terminal.close_trade(trade['symbol'], trade['position_id'], 0, self.bot_number, True)

                if is_sl_update(text):
                    ficus_logger.info(f"Update stop loss to entry for {symbol}")
                    print(f"Update stop loss to entry for {symbol}")
                    self.terminal.update_stop_loss(trade['symbol'], trade['position_id'])
        else:
            ficus_logger.warning("Could not find a symbol for reply message.")
            print("Could not find a symbol for reply message.")

    async def start_listening(self):
        await self.client.start(self.__PHONE_NUMBER)
        ficus_logger.info("TelegramBot started")
        print("TelegramBot started")
        await self.client.run_until_disconnected()

# if __name__ == '__main__':
#     handler = TelegramEventHandler()
#     with handler.client:
#         handler.client.loop.run_until_complete(handler.start_listening())
