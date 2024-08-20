import asyncio

from ficus.main.terminal_provider import provide_trading_terminal
from ficus.metatrader.FicusTrader import FicusTrader
from ficus.metatrader.MemoryStorage import MemoryStorage
from ficus.metatrader.MetatraderTerminal import MetatraderTerminal
from ficus.signals.TelegramBot import TelegramBot

# define the magic nr
__TRADER_BOT_MAGIC_NR = 2341004
# power on the terminal
terminal = provide_trading_terminal()
# init the memory; sync the memory with the terminal
storage = MemoryStorage()
storage.sync_terminal()
# start the trading bot
trader = FicusTrader(terminal, storage, __TRADER_BOT_MAGIC_NR)
# start the telegram bot
telegram_bot = TelegramBot(terminal, storage, __TRADER_BOT_MAGIC_NR)
# in the future, start a UI here as well for ease of use.


async def main():
    task1 = asyncio.create_task(telegram_bot.start_listening())
    task2 = asyncio.create_task(trader.monitor_active_trades())
    await asyncio.gather(task1, task2)

if __name__ == '__main__':
    terminal.init()
    with telegram_bot.client:
        telegram_bot.client.loop.run_until_complete(main())
