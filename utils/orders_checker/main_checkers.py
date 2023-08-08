import asyncio
import logging
from datetime import datetime, timezone, timedelta

from aiogram import types

from data.config import TIMEZONE
from keyboards import send_order_inline
from utils import generate_wallet_async, get_balance_async, \
    withdraw_async, check_transaction_async, remove_wallet_async, decrypt_async, notify_admins
from utils.bot_funcs import create_order_m_text, add_backslash, create_order_b_text, send_product_images, \
    add_backslashes
from utils.db_api.models import Stock, Order


# Pending payments checker
async def check_pending_payments(dp):
    logging.info("Started checking pending payments.")
    while True:
        orders = await Order.filter(status='pending_payment').all()
        for order in orders:
            user = await order.user
            utc = timezone(timedelta(hours=TIMEZONE))
            created_at_local = order.created_at.astimezone(utc)
            now_local = datetime.now(utc)
            print(timedelta(minutes=3))
            if now_local - created_at_local >= timedelta(minutes=3):
                text = await create_order_m_text(order, "Expired")
                text += f"Order expired\. To return to the menu, press /start"
                if order.type == 0:
                    user.false_orders += 1
                    product = await order.product
                    country = await product.country
                    category = await product.category
                    d_method = await product.d_method
                    await Stock.create(
                        product=product,
                        quantity=order.quantity,
                        d_type=product.d_type,
                        category=category,
                        country=country,
                        d_method=d_method
                    )
                await dp.bot.edit_message_text(
                    text,
                    chat_id=user.tg_id,
                    message_id=order.message_id,
                    parse_mode=types.ParseMode.MARKDOWN_V2,
                    reply_markup=None
                )
                user.active_order = False
                await order.delete()
            else:
                balance = await get_balance_async(user.wallet)
                if balance == order.price:
                    order.status = "paid"
                    if order.type != 2:
                        user.balance -= order.to_balance
                        user.coupon -= order.to_coupon
                        text = await create_order_m_text(order, "Paid")
                        text += f"Paid: *{await add_backslash(order.price)} LTC*\n"
                        if order.to_balance > 0:
                            text += f"From balance: *${order.to_balance}*\n"
                        if order.to_coupon > 0:
                            text += f"From coupon: *${order.to_coupon}*\n"
                        text += f"\n➖➖➖➖➖➖➖➖➖➖➖➖\n\n" \
                                f"Order is paid and being processed\."
                    else:
                        user.balance += order.to_balance
                        text = await create_order_m_text(order, "Paid")
                        text += f"Paid: *{await add_backslash(order.price)} LTC*\n\n➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
                        text += f"Transfer received and accepted for processing\."
                    await dp.bot.delete_message(
                        chat_id=user.tg_id,
                        message_id=order.message_id
                    )
                    new_msg = await dp.bot.send_message(
                        chat_id=user.tg_id,
                        text=text,
                        parse_mode=types.ParseMode.MARKDOWN_V2,
                        reply_markup=None
                    )
                    order.message_id = new_msg.message_id

                    user.false_orders = 0
                    await order.save()
            await user.save()

        await asyncio.sleep(10)


# Paid orders checker
async def check_paid_orders(dp):
    logging.info("Started checking paid orders.")
    while True:
        orders = await Order.filter(status='paid').all()
        for order in orders:
            user = await order.user
            confirmed = await check_transaction_async(user.wallet, order.price)
            if order.price > 0.0 and confirmed:
                withdrawn = await withdraw_async(user.wallet, order.price)
                if withdrawn:
                    order.withdrawn = True
                    order.seed_old = withdrawn
                else:
                    order.wallet_old = user.wallet
                    order.seed_old = await decrypt_async(user.seed)
                user.spent += order.price
            if order.price > 0.0 and confirmed or order.price <= 0.0:
                await remove_wallet_async(user.wallet)
                wallet = await generate_wallet_async()
                user.wallet = wallet["address"]
                user.seed = wallet["mnemonic"]
                order.status = "withdrawn"
                user.active_order = False
                if order.type == 0:
                    status = "Paid and processed"
                    txt = f"*Order paid and processed\.*\n_Product will be sent within 5 minutes\._\n\n"
                elif order.type == 1:
                    status = "Доставляется"
                    txt = f"*Order paid and processed\.*\n_We have started preparing your product\._\n\n"
                else:
                    status = "Оплачен и обработан"
                    txt = f"*Order paid and processed\.*\n\n_Expect deposit to arrive within 5 minutes_\n"
                text = await create_order_m_text(order, status)
                txt = text + txt

                await dp.bot.delete_message(
                    chat_id=user.tg_id,
                    message_id=order.message_id
                )
                new_msg = await dp.bot.send_message(
                    chat_id=user.tg_id,
                    text=txt,
                    parse_mode=types.ParseMode.MARKDOWN_V2,
                    reply_markup=None
                )
                order.message_id = new_msg.message_id
                await user.save()
                await order.save()


# Withdrawn orders checker
async def withdrawn_orders_checker(dp):
    logging.info("Started checking withdrawn orders.")
    while True:
        orders = await Order.filter(status='withdrawn').all()
        for order in orders:
            user = await order.user
            adm_text = await create_order_b_text(order, user)
            if order.type != 2:
                product = await order.product
                txt = "*Paid*\n\n"
                if order.to_balance > 0:
                    txt = txt + f"From balance: *`${order.to_balance}`*\n"
                if order.to_coupon > 0:
                    txt = txt + f"From coupon: *`${order.to_coupon}`*\n"
                if order.price > 0.0:
                    txt = txt + f"By LTC: *`{await add_backslash(order.price)}`*\n"
                balance_txt = txt + "\n➖➖➖➖➖➖➖➖➖➖➖➖\n\n"

                if order.type == 0:
                    text = await create_order_m_text(order, "Delivered")
                    description = await add_backslashes(product.description)
                    description = f"Description: _{description}_\n\n" \
                                  f"➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
                    user_txt = (
                        f"*Thank you for your purchase\!\n*If you have any questions, please contact support\.\n\n"
                        f"*To return to the main menu, click _/start_*")
                    user_txt = text + description + balance_txt + user_txt
                    adm_text = text + description + balance_txt + adm_text

                    await dp.bot.delete_message(user.tg_id, order.message_id)
                    await send_product_images(dp, product.id, user.tg_id, user_txt)
                    await send_product_images(dp, product.id, user.tg_id, adm_text, True)
                    await product.fetch_related('images')
                    for image in product.images:
                        await image.delete()
                    await product.delete()
                    await order.delete()
                else:
                    text = await create_order_m_text(order, "Delivery")
                    user_txt = (f"*Thank you for your order\!\n*The product about to be sent, please wait\.\n\n"
                                f"*To return to the main menu, click _/start_*")
                    keyboard = await send_order_inline(order.id)
                    user_txt = text + balance_txt + user_txt
                    adm_text = text + balance_txt + adm_text
                    await notify_admins(dp, adm_text, keyboard)
                    await dp.bot.delete_message(user.tg_id, order.message_id)
                    msg = await dp.bot.send_message(user.tg_id, user_txt, parse_mode=types.ParseMode.MARKDOWN_V2)
                    order.message_id = msg.message_id
                    order.status = "delivery"
                    await order.save()
                user.orders_no += 1
            else:
                text = await create_order_m_text(order, "Completed")
                txt = f"Paid: *`{await add_backslash(order.price)}` LTC*\n\n" \
                      f"➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
                txt_user = f"_Deposit completed\._\n\n*To return to the main menu, click _/start_*"
                txt_user = text + txt + txt_user
                adm_text = text + txt + adm_text

                await notify_admins(dp, adm_text)
                await dp.bot.delete_message(user.tg_id, order.message_id)
                await dp.bot.send_message(user.tg_id, txt_user, parse_mode=types.ParseMode.MARKDOWN_V2)
                await order.delete()

            await user.save()
