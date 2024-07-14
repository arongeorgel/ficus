import asyncio
import logging
import re
from datetime import datetime
from typing import Optional

from telegram import Update, Bot
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackContext, Application

from ficus.metatrader.MetatraderTerminal import MetatraderTerminal
from ficus.metatrader.__main__ import open_trades
from ficus.models.models import FicusTrade, BOT_NUMBER_FRED_MAIN
from ficus.models.utils import find_trade_by_tmsg
from ficus.telegram.PositionSizeCalculator import PositionSizeCalculator
from ficus.telegram.TelegramLogHandler import TelegramHandler

# Define your Telegram bot token
TELEGRAM_TOKEN = '7495868354:AAG8j_HS-wGmXz7Dr9Y-5As6hOkBGEXEYSs'
FRED_MAIN = -1001239815745
MYSELF = 6023501559

chats = [MYSELF, FRED_MAIN]

TRADE_VOLUME = 0.16

# Configure logging
logging.basicConfig(level=logging.INFO,  # Set the logging level
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Define the log message format
                    filename='app.log',  # Set the log file name
                    filemode='w'  # Set the file mode (w for overwrite, a for append)
                    )
logging.getLogger('httpx').setLevel(logging.ERROR)


async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('Trading bot started!')


def is_sl_update(text) -> bool:
    key_words = ['stop loss', 'sl entry']
    return any(arg in text.lower() for arg in key_words)


def should_close_trade_fully(text) -> bool:
    pattern = re.compile(
        r'(?i)(close\s*-\s*(-?\d+)|close\s*\(\s*(-?\d+)\s*\)|close\s+fully|fully\s+close)'
    )

    # Search for the pattern in the text
    match = pattern.search(text)
    return True if match else False


def line_is_int(line):
    try:
        int(line)
        return True
    except ValueError:
        return False


def parse_trade_message(message, message_id) -> Optional[FicusTrade]:
    position_calculator = PositionSizeCalculator()
    lines = message.strip().split('\n')
    trade = {'action': None, 'symbol': None, 'entry': None, 'sl': None, 'tps': []}
    pattern = re.compile(r'\b\d+\.?\d*\b')
    for line in lines:
        if re.search(r'(\b(?:buy|sell)\b)', line, re.IGNORECASE):
            trade['action'] = re.search(r'(\b(?:buy|sell)\b)', line, re.IGNORECASE).group().lower()
            symbol_match = re.search(r'(\b\w{6}\b)', line.upper())
            if symbol_match is not None:
                trade['symbol'] = symbol_match.group().upper()
            else:
                break
        elif line.lower().startswith('enter') or line.lower().startswith('entry') or (
                trade['action'] is not None and line_is_int(line)):
            match = re.search(pattern, line)
            trade['entry'] = float(match.group())
        elif line.lower().startswith('sl'):
            match = re.search(pattern, line)
            if match:
                trade['sl'] = float(match.group())
        elif line.lower().startswith('tp'):
            match = re.search(pattern, line)
            trade['tps'].append(float(match.group()))

    if trade['action'] == 'buy':
        trade['tps'].sort()
    elif trade['action'] == 'sell':
        trade['tps'].sort(reverse=True)

    if trade['action'] is None or trade['sl'] is None or trade['entry'] is None:
        return None

    trade['volume'] = position_calculator.forex_calculator(
        trade['symbol'],
        trade['entry'],
        trade['sl'],
        2000,
        2)

    return FicusTrade(
        symbol=trade['symbol'],
        trade_direction=trade['action'],
        entry_price=trade['entry'],
        stop_loss_price=trade['sl'],
        take_profits=trade['tps'],
        take_profits_hit=[False, False, False, False],
        start_volume=trade['volume'],
        position_id=None,
        message_id=message_id,
        volume=trade['volume']
    )


def extract_trade_symbol(reply_message_text):
    original_message = reply_message_text
    original_trade = parse_trade_message(original_message)
    return original_trade['symbol'] if original_trade is not None else None


async def handle_message(update: Update, context: CallbackContext):
    if update.message.chat_id not in chats:
        logging.warning("Message from unknown chat ID: %s", update.message.chat_id)
        return

    text = update.message.text
    symbol = extract_trade_symbol(
        update.message.reply_to_message.text) if update.message.reply_to_message is not None else None

    if symbol is not None:
        message_id = update.message.reply_to_message.message_id
        trade = find_trade_by_tmsg(open_trades, message_id)

        if trade is None:
            logging.error(f"Cound not find an open trade for {text}")
        else:
            if should_close_trade_fully(text):
                print(f"Closing trade fully for {symbol}")
                MetatraderTerminal.close_trade(symbol, trade['position_id'], True)

        if is_sl_update(text):
            print(f"Update stop loss to entry for {symbol}")
            MetatraderTerminal.set_sl_to_entry(symbol, trade['position_id'])
    else:
        trade = parse_trade_message(text, update.message.message_id)
        if trade is not None:
            print(f'Executing trade: {trade}')
            MetatraderTerminal.execute_pending_trade(trade, BOT_NUMBER_FRED_MAIN)


async def start_telegram_bot():
    bot = Bot(token=TELEGRAM_TOKEN)
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    telegram_handler = TelegramHandler(bot, MYSELF)
    logging.getLogger().addHandler(telegram_handler)

    await application.initialize()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await application.start()
    await application.updater.start_polling()

    while True:
        now = datetime.now()
        start_time = now.replace(hour=1, minute=0, second=0, microsecond=0)
        end_time = now.replace(hour=23, minute=0, second=0, microsecond=0)

        if now.weekday() == 0 and now >= start_time:
            # logging.info("Starting trading bot operations for the week.")
            print("week")
        elif now.weekday() == 4 and now >= end_time:
            logging.info("Stopping trading bot operations for the weekend.")
            break

        await asyncio.sleep(60)  # Check every minute


if __name__ == '__main__':
    asyncio.run(start_telegram_bot())
