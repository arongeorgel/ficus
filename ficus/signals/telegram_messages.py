import re

from ficus.signals.message_parser import parse_trade_message

# Define your Telegram bot token
TELEGRAM_TOKEN = '7495868354:AAG8j_HS-wGmXz7Dr9Y-5As6hOkBGEXEYSs'
FRED_MAIN = -1001239815745
MYSELF = 6023501559

chats = [MYSELF, FRED_MAIN]



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


def extract_trade_symbol(reply_message_text, message_id):
    original_message = reply_message_text
    original_trade = parse_trade_message(original_message, message_id)
    return original_trade['symbol'] if original_trade is not None else None


