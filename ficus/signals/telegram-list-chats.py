import asyncio
from datetime import datetime, timedelta

from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel

from ficus.signals.telegram_messages import FRED_MAIN, parse_trade_message

# Replace these with your own values from https://my.telegram.org
api_id = 21257186
api_hash = '71bf8d6d969e25ddba66fdc1fd0c50c6'
phone_number = '+31610833394'


def clean_message(message):
    # Remove all empty lines
    cleaned_message = "\n".join(line for line in message.splitlines() if line.strip())
    return cleaned_message


async def fetch_messages(client: TelegramClient):
    # Calculate the timestamp for two months ago
    date_60_days_ago = datetime.now() - timedelta(days=60)

    # Fetch messages from the chat
    # Fetch the chat
    peer = PeerChannel(int(FRED_MAIN))

    # Fetch messages without a limit using pagination
    offset_id = 0
    all_messages = []

    while True:
        history = await client(GetHistoryRequest(
            peer=peer,
            offset_id=offset_id,
            offset_date=None,
            add_offset=0,
            limit=100,  # Fetching in chunks of 100 messages
            max_id=0,
            min_id=0,
            hash=0
        ))

        messages = history.messages
        if not messages:
            break

        all_messages.extend(messages)
        offset_id = messages[-1].id

        # Break the loop if the messages are older than 60 days
        if messages[-1].date.replace(tzinfo=None) < date_60_days_ago:
            break

    # Reverse the list to have messages from oldest to newest
    all_messages.reverse()

    counter = 0
    for message in all_messages:
        text = message.raw_text

        if text is not None and message.reply_to is None:
            try:
                trade = parse_trade_message(text, message.id)
                if trade is not None and trade['entry_price'] is not None:
                    counter = counter + 1

                    print(f'({counter}) {message.date}: {trade}')
            except Exception:
                continue


async def fetch_chats(client: TelegramClient):
    chats = await client.get_dialogs()
    for chat in chats:
        print(f'Name: {chat.name} | ID: {chat.id}')


async def prepare_client():
    # Create the client and connect
    client = TelegramClient('session_name', api_id, api_hash)
    await client.start(phone_number)

    # await fetch_chats(client)
    await fetch_messages(client)

    # Disconnect the client
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(prepare_client())
