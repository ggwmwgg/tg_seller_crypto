import asyncio

from aiogram import types
from aiogram.types import ReplyKeyboardRemove
from loader import dp


# Unknown command handler
@dp.message_handler(state="*")
async def bot_echo(message: types.Message):
    await message.delete()
    text = "Unknown command\nPress /start to restart the bot"
    await asyncio.sleep(5)
    msg = await message.answer(text, reply_markup=ReplyKeyboardRemove())
    await msg.delete()
