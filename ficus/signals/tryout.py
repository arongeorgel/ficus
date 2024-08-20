import re
from typing import Optional, List

from ficus.signals.message_parser import parse_trade_message

message_text = '''💹 BUY GBPAUD
👉 Entry: 1.92889
🚀 Lot size: 0.14
💎 TP: 1.93090 (19.0$ - 20.1 pip)
💎 TP2: 1.93290 (38.0$ - 40.1 pip)
💎 TP3: 1.93690 (76.0$ - 80.1 pip)
🔶 S/L: 1.92670 (21.0$ - 21.9 pip)
💰 Risk 2% - 1000$'''

trade = parse_trade_message(message_text, 'msg1')
print(trade)

# print(f'Action: {trade.action}')
print(f'Symbol: {trade.symbol}')
print(f'Entry: {trade.entry}')
print(f'SL: {trade.stop_loss}')
print(f'TP: {trade.tps}')


####

