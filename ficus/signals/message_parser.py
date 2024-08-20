import re
from typing import Optional, List

from ficus.models.logger import ficus_logger
from ficus.models.models import FicusTrade, get_vantage_trading_symbol
from ficus.signals.PositionSizeCalculator import PositionSizeCalculator


def line_is_int(line) -> bool:
    try:
        int(line)
        return True
    except ValueError:
        return False


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


def parse_trade_message(message_text: str, message_id: str, is_reply) -> Optional[FicusTrade]:
    position_calculator = PositionSizeCalculator()
    lines = message_text.strip().split('\n')
    action: Optional[str] = None
    symbol: Optional[str] = None
    entry: Optional[float] = None
    stop_loss: Optional[float] = None
    tps: List[float] = list()

    pattern = re.compile(r'\b\d+\.?\d*\b')
    for line in lines:
        search_match = re.search(r'(\b(?:buy|sell)\b)', line, re.IGNORECASE)
        if search_match:
            action = search_match.group().lower()
            symbol_match = re.search(r'(\b\w{6}\b)', line.upper())
            if symbol_match is not None:
                symbol = symbol_match.group().upper()
            else:
                break
        elif (line.lower().startswith('enter')
              or line.lower().startswith('entry')
              or line.lower()[2:].startswith('entry')
              or (action is not None and line_is_int(line))):
            match = re.search(pattern, line)
            if match:
                entry = float(match.group())
        elif line.lower().startswith('sl') or line.lower()[2:].startswith('s/l'):
            match = re.search(pattern, line)
            if match:
                stop_loss = float(match.group())
        elif line.lower().startswith('tp') or line.lower()[2:].startswith('tp'):
            match = re.search(pattern, line)
            if match:
                tps.append(float(match.group()))

    if action == 'buy':
        tps.sort()
    elif action == 'sell':
        tps.sort(reverse=True)

    if action is None or stop_loss is None or entry is None or symbol is None:
        print(f"Failed to parse message {message_text} to trade.")
        ficus_logger.info(f"Failed to parse message {message_text} to trade.")
        ficus_logger.info("===============================================\n")
        return None

    volume = position_calculator.forex_calculator(
        symbol,
        entry,
        stop_loss,
        2000,
        5,
        False)

    trade = FicusTrade(
        symbol=get_vantage_trading_symbol(symbol),
        trade_direction=action,
        entry_price=entry,
        stop_loss_price=stop_loss,
        take_profits=tps,
        take_profits_hit=[False, False, False, False],
        start_volume=volume,
        position_id=None,
        message_id=message_id,
        volume=volume
    )

    if not is_reply:
        print(f"Parsed successfully the message to trade {trade}")
        ficus_logger.info(f"Parsed successfully the message to trade {trade}")
    return trade


def extract_trade_symbol(message_text, message_id, is_reply):
    original_trade = parse_trade_message(message_text, message_id, is_reply)
    return original_trade['symbol'] if original_trade is not None else None
