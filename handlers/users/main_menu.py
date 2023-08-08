import asyncio
import math

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Regexp

from keyboards import back, yes_no, order_cancel_inline, m_m_inline
from loader import dp
from states.main import Main, Orders
from utils import create_m_m_text, add_backslash
from utils.bot_funcs import create_order_m_text, add_backslashes, get_showcase
from utils.db_api.models import User, Order, Coupons
from utils.misc import rate_limit
from utils.wallet import get_ltc_price_async


# Deposit handler
@rate_limit(1, 'deposit')
@dp.callback_query_handler(Regexp(r"confirmation:no"), state=Main.deposit)
@dp.callback_query_handler(Regexp(r"deposit"), state=Main.main)
@dp.callback_query_handler(Regexp(r"deposit"), state=None)
async def deposit_callback(query: types.CallbackQuery, state: FSMContext):
    user = await User.get_or_none(tg_id=query.from_user.id)
    message_id = query.message.message_id
    txt = (f"_*Enter desired amount to deposit:*_\n"
           f"_Example: 10 \(for deposit $10\)_\n"
           f"_Minimum deposit amount: $1_")
    text = await create_m_m_text(user, txt)

    await query.message.edit_caption(
        caption=text,
        parse_mode=types.ParseMode.MARKDOWN_V2,
        reply_markup=back
    )
    await state.update_data(message_id=message_id)
    await Main.deposit.set()


# Deposit handler amount
@rate_limit(1, 'deposit_n')
@dp.message_handler(state=Main.deposit)
async def deposit(message: types.Message, state: FSMContext):
    data = await state.get_data()
    message_id = data.get("message_id")
    user = await User.get_or_none(tg_id=message.from_user.id)
    msg_txt = message.text
    invalid_txt = (f"_*Enter valid amount, example:*_ *10* \(for deposit $10\)_\n"
                   f"_Minimum deposit amount: $1_\n"
                   f"_*Invalid amount, try again:*_")
    invalid_txt = await create_m_m_text(user, invalid_txt)
    await message.delete()
    if msg_txt.startswith("$"):
        msg_txt = msg_txt[1:]
    elif msg_txt.endswith("$"):
        msg_txt = msg_txt[:-1]
    try:
        amount = int(msg_txt)
        if amount < 1:
            raise ValueError
        else:

            price = await get_ltc_price_async(amount)
            price = price + (price * 0.02)
            price = math.ceil(price * 1000) / 1000
            txt = (f"*Order confirmation:*\n\n"
                   f"Type: *Deposit*\n"
                   f"Amount: *${amount}*\n\n"
                   f"➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
                   f"Total: *_`{await add_backslash(price)}`_ LTC*\n\n"
                   f"➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
                   f"*_Attention\! After confirmation, 30 minutes will be allocated for payment, after order will be expired\._*\n"
                   f"\n_Confirm order?_")
            await state.update_data(
                price_ltc=price,
                price_usd=amount
            )
            msg_new = await dp.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=message_id,
                caption=txt,
                parse_mode=types.ParseMode.MARKDOWN_V2,
                reply_markup=yes_no
            )
            await asyncio.sleep(300)
            if "Confirm order?" in msg_new.caption:
                await msg_new.delete()
    except ValueError:
        try:
            await dp.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=message_id,
                caption=invalid_txt,
                parse_mode=types.ParseMode.MARKDOWN_V2,
                reply_markup=back
            )
        except Exception as e:
            pass


# Deposit handler final (confirmation)
@rate_limit(1, 'deposit_y')
@dp.callback_query_handler(Regexp(r"confirmation:yes"), state=Main.deposit)
async def deposit_confirmation(query: types.CallbackQuery, state: FSMContext):
    user = await User.get_or_none(tg_id=query.from_user.id)
    user.active_order = True
    data = await state.get_data()
    price_ltc = data.get("price_ltc")
    price_usd = data.get("price_usd")
    await query.message.delete()
    order = await Order.create(
        user=user,
        type=2,
        price=price_ltc,
        to_balance=price_usd
    )
    keyboard = await order_cancel_inline(order.id)
    txt = await create_order_m_text(order, "Pending payment")
    text_price = (f"Total: *`{await add_backslash(price_ltc)}`* $\n"
                  f"To wallet: *`{user.wallet}`*\n\n"
                  f"➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
                  f"Order created and waiting for payment\.\n"
                  f"Balance will be replenished within 1\-5 minutes after payment is received\.\n\n"
                  f"➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
                  f"*_Attention\! After confirmation, 30 minutes will be allocated for payment, after order will be expired\._*\n")
    txt = txt + text_price
    msg = await dp.bot.send_message(
        chat_id=query.from_user.id,
        text=txt,
        parse_mode=types.ParseMode.MARKDOWN_V2,
        reply_markup=keyboard
    )
    order.message_id = msg.message_id
    order.status = "pending_payment"
    await order.save()
    await user.save()
    await state.reset_data()
    await Orders.pending_payment.set()


# Coupon handler code
@rate_limit(1, 'coupon_ask')
@dp.callback_query_handler(Regexp(r"coupon_add"), state=Main.main)
@dp.callback_query_handler(Regexp(r"coupon_add"), state=None)
async def coupon_add(query: types.CallbackQuery, state: FSMContext):
    user = await User.get_or_none(tg_id=query.from_user.id)
    text = await create_m_m_text(user, "_Enter coupon:_")
    await query.message.edit_caption(
        caption=text,
        parse_mode=types.ParseMode.MARKDOWN_V2,
        reply_markup=back
    )
    msg = query.message
    await state.update_data(msg=msg.message_id)
    await Main.coupon.set()


# Coupon handler final
@rate_limit(1, 'coupon_add')
@dp.message_handler(state=Main.coupon)
async def coupon_add(message: types.Message, state: FSMContext):
    data = await state.get_data()
    message_id = data.get("msg")
    user = await User.get_or_none(tg_id=message.from_user.id)
    coupon = message.text
    used_coupon = await user.used_coupons.filter(code=coupon).first()
    if used_coupon:
        text_coupon = f"*Coupon \(`{message.text}`\) already used\!*\n\n_Enter another coupon\:_"
        text = await create_m_m_text(user, text_coupon)
        await dp.bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=message_id,
            caption=text,
            parse_mode=types.ParseMode.MARKDOWN_V2,
            reply_markup=back
        )
    else:
        coupon = await Coupons.get_or_none(code=coupon)
        if coupon is not None:
            if coupon.usages_left > 0:
                await user.used_coupons.add(coupon)
                user.coupon += coupon.amount
                await user.save()
                coupon.usages_left -= 1
                await coupon.save()
                keyboard = await m_m_inline()
                text_coupon = f"*Coupon \(`{message.text}`\) successfully activated\!*\n\n_Where we go next?_"
                text = await create_m_m_text(user, text_coupon)
                await dp.bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=message_id,
                    caption=text,
                    parse_mode=types.ParseMode.MARKDOWN_V2,
                    reply_markup=keyboard
                )
                await Main.main.set()
            else:
                text_coupon = f"*Coupon \(`{message.text}`\) expired\!*\n\n_Enter another coupon\:_"
                text = await create_m_m_text(user, text_coupon)
                await dp.bot.edit_message_caption(
                    chat_id=message.chat.id,
                    message_id=message_id,
                    caption=text,
                    parse_mode=types.ParseMode.MARKDOWN_V2,
                    reply_markup=back
                )
        else:
            text_coupon = f"*Coupon \(`{message.text}`\) not found\!*\n\n_Enter another coupon\:_"
            text = await create_m_m_text(user, text_coupon)
            await dp.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=message_id,
                caption=text,
                parse_mode=types.ParseMode.MARKDOWN_V2,
                reply_markup=back
            )
        await message.delete()


# Rules handler
@rate_limit(1, 'rules')
@dp.callback_query_handler(Regexp(r"rules"), state=Main.main)
@dp.callback_query_handler(Regexp(r"rules"), state=None)
async def rules(query: types.CallbackQuery):
    text = (f"*Rules:*\n\n"
            f"- Rule 1\n\n"
            f"- Rule 2\n\n"
            f"- Rule 3")
    text = await add_backslashes(text)
    await query.message.edit_caption(
        caption=text,
        parse_mode=types.ParseMode.MARKDOWN_V2,
        reply_markup=back
    )
    await Main.rules.set()


# Showcase handler
@rate_limit(1, 'showcase')
@dp.callback_query_handler(Regexp(r"showcase"), state=Main.main)
@dp.callback_query_handler(Regexp(r"showcase"), state=None)
async def showcase(query: types.CallbackQuery):
    txt = await get_showcase(True, False)
    await query.message.edit_caption(
        caption=txt,
        parse_mode=types.ParseMode.MARKDOWN_V2,
        reply_markup=back
    )

    await Main.showcase.set()
