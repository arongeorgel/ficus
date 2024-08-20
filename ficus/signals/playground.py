import asyncio
import datetime
import traceback
from telethon import TelegramClient, events


class TelegramEventHandler:
    __TELEGRAM_TOKEN = '7495868354:AAG8j_HS-wGmXz7Dr9Y-5As6hOkBGEXEYSs'
    __FRED_MAIN = -1001239815745
    __MYSELF = 6023501559

    __API_ID = 21257186
    __API_HASH = '71bf8d6d969e25ddba66fdc1fd0c50c6'
    __PHONE_NUMBER = '+31610833394'

    def __init__(self):
        self.client = TelegramClient('ficus-trader', self.__API_ID, self.__API_HASH)
        self.phone_number = self.__PHONE_NUMBER

        # Register the event handler
        self.client.on(events.NewMessage)(self.handler)

    async def handler(self, event):
        chat = await event.get_chat()
        if chat.id == 1622898322 or chat.id == 1465548315:
            return

        print(f'==========         [{datetime.datetime.now().strftime("%A %H:%M")}]         =========')
        try:
            message = event.message
            if hasattr(message, 'is_reply') and message.is_reply:
                original_message = await message.get_reply_message()
                self.handle_text_message(message.raw_text, message.id, True, original_message.raw_text, original_message.id)
            else:
                self.handle_text_message(message.raw_text, message.id, False, "")
        except Exception:
            print('----  traceback  ----')
            print(traceback.format_exc())
            print('---------------------')

        print("=============================================================\n")

    def handle_text_message(self, message_text, message_id, is_reply, original_text, original_id=None):
        # Implement your message handling logic here
        print(f"Message ID: {message_id}, Text: {message_text}")
        if is_reply:
            print(f"Reply to Message ID: {original_id}, Original Text: {original_text}")
        # Additional processing can be added here

    async def start_listening(self):
        await self.client.start(self.phone_number)
        print("Client Created")
        await self.client.run_until_disconnected()


if __name__ == '__main__':
    handler = TelegramEventHandler()
    with handler.client:
        handler.client.loop.run_until_complete(handler.start_listening())