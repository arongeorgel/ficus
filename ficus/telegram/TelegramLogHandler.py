import asyncio
import logging


class TelegramHandler(logging.Handler):
    def __init__(self, bot, chat_id):
        super().__init__()
        self.bot = bot
        self.chat_id = chat_id

    def emit(self, record):
        log_entry = self.format(record)
        asyncio.create_task(self.send_log_message(log_entry))

    async def send_log_message(self, log_entry):
        await self.bot.send_message(chat_id=self.chat_id, text=log_entry)