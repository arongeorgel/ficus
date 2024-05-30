import spacy
import re

nlp = spacy.load("en_core_web_sm")

# The input string
text = """
GBPJPY Sell now
Enter 196.460
SL 197.360 (90)
TP1 196.060
TP2 195.460
TP3 194.060
TP4 190.960 (550)
"""

# Tokenization and pattern matching
lines = text.strip().split('\n')
data = {}

# Regular expressions for matching patterns
entry_pattern = re.compile(r'Enter (\d+\.\d+)')
sl_pattern = re.compile(r'SL (\d+\.\d+) \((\d+)\)')
tp_pattern = re.compile(r'TP(\d+) (\d+\.\d+)(?: \((\d+)\))?')

for line in lines:
    if 'Sell' in line or 'Buy' in line:
        data['Currency Pair'], data['Action'] = line.split()[:2]
    elif entry_pattern.search(line):
        data['Entry Price'] = entry_pattern.search(line).group(1)
    elif sl_pattern.search(line):
        sl_match = sl_pattern.search(line)
        data['Stop Loss'] = {'Price': sl_match.group(1), 'Pips': sl_match.group(2)}
    elif tp_pattern.search(line):
        tp_match = tp_pattern.search(line)
        tp_key = f'Take Profit {tp_match.group(1)}'
        tp_value = {'Price': tp_match.group(2)}
        if tp_match.group(3):
            tp_value['Pips'] = tp_match.group(3)
        data[tp_key] = tp_value

# Print the extracted data
print(data)
