import datetime
import re
from dataclasses import dataclass
from enum import Enum
from typing import List

from telethon import TelegramClient  # type: ignore

# Remember to use your own values from my.telegram.org!
api_id = 21257186 # fred main channel
api_hash = '71bf8d6d969e25ddba66fdc1fd0c50c6'

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
    CLOSE = 3


@dataclass(frozen=True)
class Trade:
    id: int
    currency_pair: str
    trade_action: TradeAction
    entry_price: float
    stop_loss_price: float
    profits_list: List[float]


def classify_message(text):
    if "buy now" in text.lower():
        return TradeAction.BUY
    elif "sell now" in text.lower():
        return TradeAction.SELL
    elif "close fully" in text.lower():
        return TradeAction.CLOSE
    return None


def extract_trade(text, msg_type, msg_id):
    try:
        trade = Trade(
            id=msg_id,
            currency_pair=re.findall(r'[A-Za-z]{6}', text)[0],
            trade_action=msg_type,
            entry_price=float(re.findall(r'enter (\d+(\.\d+)?)', text, re.IGNORECASE)[0][0]),
            stop_loss_price=float(re.findall(r'sl (\d+(\.\d+)?)', text, re.IGNORECASE)[0][0]),
            profits_list=[float(tp[0]) for tp in re.findall(r'tp\d (\d+(\.\d+)?)', text, re.IGNORECASE)],
        )
        return trade

    except IndexError:
        pass
        return None


def action_for_broker(trade: Trade):
    if trade.trade_action == TradeAction.BUY:
        print(f"[{trade.id}] Buying {trade.currency_pair} at {trade.entry_price}. "
              f"Stop loss set at {trade.stop_loss_price}"
              f" and profits set for {trade.profits_list}")
    elif trade.trade_action == TradeAction.SELL:
        print(f"[{trade.id}] Selling {trade.currency_pair} at {trade.entry_price}. "
              f"Stop loss set at {trade.stop_loss_price}"
              f" and profits set for {trade.profits_list}")
    elif trade.trade_action == TradeAction.CLOSE:
        print(f"[{trade.id}] Closing {trade.currency_pair}")


def date_format(message):
    if type(message) is datetime:
        return message.strftime("%Y-%m-%d %H:%M:%S")


async def get_reply_message_id(message):
    # Check if the message is a reply
    if message.reply_to is not None and message.reply_to.reply_to_msg_id:
        # Return the ID of the replied-to message
        return message.reply_to_msg_id
    else:
        # If there is no reply, return None or an appropriate value
        return None


async def get_dialogs(client):
    # Get all the dialogs (chats)
    dialogs = await client.get_dialogs()
    for dialog in dialogs:
        print(dialog)


async def main():
    async with TelegramClient('session_name', api_id, api_hash) as client:
        await client.start()

        async for msg in client.iter_messages(int("1239815745"), limit=100):
            pp_message = preprocess_text(msg.message)

            trade_action = classify_message(pp_message) if pp_message else None

            trades = {}

            if trade_action == TradeAction.BUY or trade_action == TradeAction.SELL:
                trade = extract_trade(pp_message, trade_action, msg.id) if pp_message else None
                if trade:
                    trades[msg.id] = trade
                    action_for_broker(trade)

            if trade_action == TradeAction.CLOSE:
                reply_id = await get_reply_message_id(msg)
                if reply_id in trades:
                    trade = trades[msg.id]
                    action_for_broker(trade)


if __name__ == '__main__':
    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
