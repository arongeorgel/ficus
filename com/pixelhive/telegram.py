import datetime
import re
import string

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Type

from telethon import TelegramClient

# Remember to use your own values from my.telegram.org!
api_id = 21257186
api_hash = '71bf8d6d969e25ddba66fdc1fd0c50c6'


# client = TelegramClient('anon', api_id, api_hash)


# @client.on(events.NewMessage(chats='GoldViewFX'))
# async def my_event_handler(event):
#     print(event.raw_text)

def preprocess_text(text):
    if text is not None:
        text = re.sub(r'\s+', ' ', text.strip())
        return text


class TradeAction(Enum):
    BUY = 1
    SELL = 2
    SL_TO_ENTRY = 3
    CLOSE = 4


@dataclass
class Trade:
    id: int
    currencyPair: string
    tradeAction: TradeAction
    entryPrice: float
    stopLossPrice: float
    profits: []

    def __init__(self):
        super().__init__()


def classify_message(text):
    if "buy now" in text.lower():
        return TradeAction.BUY
    elif "sell now" in text.lower():
        return TradeAction.SELL
    elif "sl entry" in text.lower():
        return TradeAction.SL_TO_ENTRY
    elif "close fully" in text.lower():
        return TradeAction.CLOSE
    return None


def extract_trade(text, msg_type, msg_id) -> Optional[Trade]:
    try:
        if msg_type == TradeAction.BUY or msg_type == TradeAction.SELL:
            trade = Trade()
            trade.id = msg_id
            trade.currencyPair = re.findall(r'[A-Za-z]{6}', text)[0]
            trade.tradeAction = msg_type
            trade.entryPrice = float(re.findall(r'enter (\d+(\.\d+)?)', text, re.IGNORECASE)[0][0])
            trade.stopLossPrice = float(re.findall(r'sl (\d+(\.\d+)?)', text, re.IGNORECASE)[0][0])
            trade.profits = [float(tp[0]) for tp in re.findall(r'tp\d (\d+(\.\d+)?)', text, re.IGNORECASE)]
            return trade

    except IndexError:
        pass
        return None


def action_for_broker(trade: Trade):
    if trade.tradeAction == TradeAction.BUY:
        print(f"[{trade.id}] Buying {trade.currencyPair} at {trade.entryPrice}. Stop loss set at {trade.stopLossPrice}"
              f" and profits set for {trade.profits}")
    elif trade.tradeAction == TradeAction.SELL:
        print(f"[{trade.id}] Selling {trade.currencyPair} at {trade.entryPrice}. Stop loss set at {trade.stopLossPrice}"
              f" and profits set for {trade.profits}")
    elif trade.tradeAction == TradeAction.CLOSE:
        print(f"[{trade.id}] Closing {trade.currencyPair}")
    elif trade.tradeAction == TradeAction.SL_TO_ENTRY:
        print(f"[{trade.id}] Updating SL of {trade.currencyPair} to {trade.entryPrice}")


def date_format(message):
    if type(message) is datetime:
        return message.strftime("%Y-%m-%d %H:%M:%S")


async def main():
    async with TelegramClient('session_name', api_id, api_hash) as client:
        await client.start()

        # Get all the dialogs (chats)
        # dialogs = await client.get_dialogs()
        # for dialog in dialogs:
        #    print(dialog)

        messages = client.iter_messages(int("1239815745"), limit=1000)

        async for msg in messages:
            pp_message = preprocess_text(msg.message)
            print(type(pp_message))
            if msg is not None:
                trade_action = classify_message(pp_message)
                trade = extract_trade(pp_message, trade_action, msg.id)
                if trade is not None:
                    action_for_broker(trade)


if __name__ == '__main__':
    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
