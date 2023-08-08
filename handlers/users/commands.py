from aiogram import types
from aiogram.dispatcher.filters import Command

from keyboards import main_menu_adm
from loader import dp
from states.main_adm import Admin
from utils.db_api import test_db_entries
from utils.db_api.models import User


# Admin menu entry
@dp.message_handler(Command("admin"), state="*")
async def manager_add(message: types.Message):
    user = await User.get_or_none(tg_id=message.from_user.id)
    if user.role == "admin":
        await dp.bot.send_message(
            message.from_user.id,
            "Choose an action:",
            reply_markup=main_menu_adm,
            parse_mode=types.ParseMode.MARKDOWN_V2
        )
        await message.delete()
    await Admin.main.set()


# Adding test entries to the database
@dp.message_handler(Command("test"), state="*")
async def test_db(message: types.Message):
    await test_db_entries()
    await message.delete()
