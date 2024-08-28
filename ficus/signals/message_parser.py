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


def parse_trade_message(message_text: str, message_id: str, usd_rate_func) -> Optional[FicusTrade]:
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

    if action is None or entry is None or symbol is None:
        error_message = f"Could not find any action, entry or symbol while parsing."
        print(error_message)
        ficus_logger.info(error_message)
        return None

    if stop_loss is None:
        if symbol == 'XAUUSD':
            # Set a default stop loss for XAUUSD if not provided
            stop_loss = entry - 9 if action == 'buy' else entry + 9
        else:
            error_message = f"No stop loss set for {symbol}"
            print(error_message)
            ficus_logger.info(error_message)
            return None

    if not tps:
        tp_base = entry + (3 if action == 'buy' else -3)
        tps = [tp_base, tp_base + (3 if action == 'buy' else -3),
               tp_base + (15 if action == 'buy' else -15),
               tp_base + (39 if action == 'buy' else -39)]

    if not symbol.endswith('USD'):
        usd_conversion_rate = usd_rate_func(symbol, action, False)
    else:
        usd_conversion_rate = 0

    volume = position_calculator.forex_calculator(
        symbol,
        entry,
        stop_loss,
        2000,
        5,
        usd_conversion_rate
    )

    # Sort TPs based on action
    tps.sort(reverse=(action == 'sell'))

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

    return trade


def extract_trade_symbol(message_text, message_id):
    original_trade = parse_trade_message(message_text, message_id, None)
    return original_trade['symbol'] if original_trade is not None else None
