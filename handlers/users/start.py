import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Regexp
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import ReplyKeyboardRemove

from keyboards import m_m_inline
from loader import dp
from states.main import Main, Market, Orders
from utils import create_m_m_text
from utils.bot_funcs import send_to_mm, open_image_async
from utils.db_api.models import User
from utils.misc import rate_limit


# /start handler
@rate_limit(1, key="start")
@dp.message_handler(CommandStart(), state='*')
async def bot_start(message: types.Message, state: FSMContext):
    user = await User.get_or_none(tg_id=message.from_user.id)
    await message.delete()
    if user:
        if user.active_order:
            msg_txt = "You have unprocessed orders\. Wait for them to complete or cancel\."
            msg = await dp.bot.send_message(message.chat.id, msg_txt)
            await asyncio.sleep(5)
            await msg.delete()
            await Orders.pending_payment.set()

        else:
            await dp.bot.send_chat_action(message.chat.id, "typing")
            await asyncio.sleep(3)
            keyboard = await m_m_inline()
            text_text = "_Where to go?_"
            text = await create_m_m_text(user, text_text)
            img = await open_image_async("logo.png")
            await message.answer_photo(
                img,
                caption=text,
                parse_mode=types.ParseMode.MARKDOWN_V2,
                reply_markup=keyboard)
            await state.reset_data()
            await Main.main.set()
    else:
        text = "Oops, something went wrong. Try again."
        await message.answer(text, reply_markup=ReplyKeyboardRemove())


@rate_limit(1, key="start")
@dp.callback_query_handler(Regexp(r"main:back"), state=Market.category)
@dp.callback_query_handler(Regexp(r"main:back"), state=Main.deposit)
@dp.callback_query_handler(Regexp(r"main:back"), state=Main.coupon)
@dp.callback_query_handler(Regexp(r"main:back"), state=Main.rules)
@dp.callback_query_handler(Regexp(r"main:back"), state=Main.showcase)
async def bot_start(query: types.CallbackQuery, state: FSMContext):
    state_current = await state.get_state()
    user = await User.get_or_none(tg_id=query.from_user.id)
    if user:
        text = "You already have active order. Wait for completion or cancel it."
        if state_current is not None and state_current.startswith("Order") or user.active_order:
            msg = await dp.bot.send_message(query.from_user.id, text)
            await asyncio.sleep(5)
            await msg.delete()
        else:
            await send_to_mm(query, user, state, "")
