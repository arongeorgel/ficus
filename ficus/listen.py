from telethon import TelegramClient, events
import telegram

# Remember to use your own values from my.telegram.org!
api_id = 21257186
api_hash = '71bf8d6d969e25ddba66fdc1fd0c50c6'
client = TelegramClient('anon', api_id, api_hash)


@client.on(events.NewMessage(chats=int("1239815745")))
async def my_event_handler(event):
    print(event.raw_text)
    telegram.parse_trading_message(event.raw_text)


client.start()
client.run_until_disconnected()