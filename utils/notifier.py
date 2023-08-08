import asyncio
import logging
from aiogram import Dispatcher, types
from data.config import admins


async def notify_admins(dp: Dispatcher, txt='Bot started', keyboard=None):
    """
    Notify admins about errors
    :param dp: Dispatcher
    :param txt: text message to send
    :param keyboard: keyboard to send
    :return: None
    """
    for admin in admins:
        try:
            msg = await dp.bot.send_message(admin, txt, reply_markup=keyboard, parse_mode=types.ParseMode.MARKDOWN_V2)
            await asyncio.sleep(5)
            await msg.delete()
        except Exception as err:
            logging.info(f"Error sending message to bot admin. Error: {err}")


