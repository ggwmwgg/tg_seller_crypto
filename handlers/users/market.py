import asyncio
import math

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Regexp

from keyboards import type_inline, categories_inline, quantity_inline, d_method_inline, d_type_inline, yes_no, \
    order_cancel_inline
from loader import dp
from states.main import Main, Market, Orders
from utils import create_m_m_text, add_backslash
from utils.bot_funcs import send_to_mm, open_image_async, create_order_m_text
from utils.db_api.models import User, Category, DeliveryMethod, Stock, Order, Country
from utils.misc import rate_limit
from utils.wallet import get_ltc_price_async


# Main menu => Market handler (Country selected)
@rate_limit(1, key="main_market")
@dp.callback_query_handler(Regexp(r"country:\d+"), state=Main.main)
@dp.callback_query_handler(Regexp(r"country:\d+"), state=None)
@dp.callback_query_handler(Regexp(r"category:back"), state=Market.quantity)
async def country_callback(query: types.CallbackQuery, state: FSMContext):
    user = await User.get_or_none(tg_id=query.from_user.id)
    data = await state.get_data()
    if query.data == "category:back":
        country_id = data["country"]
    else:
        country_id = int(query.data.split(":")[1])
    country = await Country.get_or_none(id=country_id)
    if country is None:
        send_to_mm_text = "Unfortunately, this product is out of stock\.\n"
        await send_to_mm(query, user, state, send_to_mm_text)
    else:

        types_s = await Stock.filter(country_id=country.id).distinct().order_by("-type").values_list("type", flat=True)
        types_list = []
        for type_s in types_s:
            types_list.append(type_s)
        keyboard = await type_inline(types_list)
        txt = f"Chosen country: *{country.name}*\n_Now choose product type:_"
        text = await create_m_m_text(user, txt)
        await query.message.edit_caption(
            text,
            parse_mode=types.ParseMode.MARKDOWN_V2,
            reply_markup=keyboard
        )
        await state.update_data(
            country=country.id,
            country_name=country.name
        )
        await Market.category.set()


# Market => Category handler
@rate_limit(1, key="market_category")
@dp.callback_query_handler(Regexp(r"type:"), state=Market.category)
@dp.callback_query_handler(Regexp(r"quantity:back"), state=Market.d_method)
async def type_callback(query: types.CallbackQuery, state: FSMContext):
    user = await User.get_or_none(tg_id=query.from_user.id)
    data = await state.get_data()
    if query.data == "quantity:back":
        type_type = str(data["type"])
    else:
        type_type = query.data.split(":")[1]
    country_id = data["country"]
    country_name = data["country_name"]
    delivery_type = None
    stocks_type = None
    if type_type == "True":
        stocks_type = True
        delivery_type = "Digital"
    elif type_type == "False":
        stocks_type = False
        delivery_type = "Preorder"
    categories = await Category.filter(
        stocks__country_id=country_id,
        stocks__type=stocks_type
    ).distinct().order_by("name").values("id", "name")
    c_list = []
    for category in categories:
        c_list.append((category["id"], category["name"]))
    if len(c_list) == 0:
        send_to_mm_text = "Unfortunately, this product is out of stock\.\n"
        await send_to_mm(query, user, state, send_to_mm_text)
    else:

        keyboard = await categories_inline(c_list)
        txt = f"Country: *{country_name}*\nChosen product type: *{delivery_type}*\n_Now choose category:_"

        text = await create_m_m_text(user, txt)

        if query.data == "quantity:back":
            await query.message.delete()
            img = await open_image_async("logo.png")
            await query.message.answer_photo(
                img,
                caption=text,
                parse_mode=types.ParseMode.MARKDOWN_V2,
                reply_markup=keyboard
            )
        else:
            await query.message.edit_caption(
                text,
                parse_mode=types.ParseMode.MARKDOWN_V2,
                reply_markup=keyboard
            )
        await state.update_data(
            type=stocks_type,
            type_name=delivery_type
        )

        await Market.quantity.set()


# Category => Quantity handler
@rate_limit(1, key="market_quantity")
@dp.callback_query_handler(Regexp(r"category:\d+"), state=Market.quantity)
@dp.callback_query_handler(Regexp(r"d_method:back"), state=Market.d_type)
async def category_callback(query: types.CallbackQuery, state: FSMContext):
    user = await User.get_or_none(tg_id=query.from_user.id)
    data = await state.get_data()
    if query.data == "d_method:back":
        category_id = data["category"]
    else:
        category_id = int(query.data.split(":")[1])
    category = await Category.get_or_none(id=category_id)
    if category:
        data = await state.get_data()
        quantities = await Stock.filter(
            country_id=data["country"],
            type=data["type"],
            category_id=category_id
        ).distinct().order_by("quantity").values_list("quantity", flat=True)
        quantities_list = []
        for quantity in quantities:
            quantities_list.append(quantity)
        txt = f"Country: *{data['country_name']}*\nProduct type: *{data['type']}*\nChosen category: *{category.name}*\n_Now choose quantity:_"
        text = await create_m_m_text(user, txt)
        keyboard = await quantity_inline(quantities_list)
        cat_photo = await category.image
        img = await open_image_async(cat_photo.url)

        await query.message.delete()
        await query.message.answer_photo(
            img,
            caption=text,
            parse_mode=types.ParseMode.MARKDOWN_V2,
            reply_markup=keyboard)

        await state.update_data(category=category_id)
        await state.update_data(category_name=category.name)
        await Market.d_method.set()
    else:
        send_to_mm_text = "Unfortunately, this product is out of stock\.\n"
        await send_to_mm(query, user, state, send_to_mm_text)


# Quantity => Delivery handler
@rate_limit(1, key="market_d_method")
@dp.callback_query_handler(Regexp(r"quantity:\d+"), state=Market.d_method)
@dp.callback_query_handler(Regexp(r"d_type:back"), state=Market.confirmation)
async def dd_type_callback(query: types.CallbackQuery, state: FSMContext):
    user = await User.get_or_none(tg_id=query.from_user.id)
    data = await state.get_data()
    if query.data == "d_type:back":
        quantity = data["quantity"]
    else:
        quantity = float(query.data.split(":")[1])

    d_methods = await DeliveryMethod.filter(
        products__stocks__country_id=data["country"],
        products__stocks__type=data["type"],
        products__stocks__category_id=data["category"],
        products__stocks__quantity=quantity
    ).distinct().prefetch_related('products__stocks')

    d_list = []
    for d_m in d_methods:
        d_list.append((d_m.id, d_m.name))
    if len(d_list) == 0:
        send_to_mm_text = "Unfortunately, this product is out of stock\.\n"
        await send_to_mm(query, user, state, send_to_mm_text)
    else:
        keyboard = await d_method_inline(d_list)
        txt = (f"Country: *{data['country_name']}*\n"
               f"Product type: *{data['type_name']}*\n"
               f"Category: *{data['category_name']}*\n"
               f"Chosen quantity: *{await add_backslash(quantity)}*\n"
               f"_Now choose the delivery method:_")
        text = await create_m_m_text(user, txt)
        await query.message.edit_caption(
            text,
            parse_mode=types.ParseMode.MARKDOWN_V2,
            reply_markup=keyboard
        )
        await state.update_data(quantity=quantity)
        await Market.d_type.set()


# Delivery method => delivery type handler
@rate_limit(1, key="market_d_type")
@dp.callback_query_handler(Regexp(r"d_method:\d+"), state=Market.d_type)
@dp.callback_query_handler(Regexp(r"confirmation:no"), state=Market.balance)
async def d_type_callback(query: types.CallbackQuery, state: FSMContext):
    user = await User.get_or_none(tg_id=query.from_user.id)
    data = await state.get_data()
    if query.data == "confirmation:no":
        d_method_id = data["d_method"]
    else:
        d_method_id = int(query.data.split(":")[1])
    delivery = await DeliveryMethod.get_or_none(id=d_method_id)
    d_types = await Stock.filter(
        country_id=data["country"],
        type=data['type'],
        category_id=data['category'],
        quantity=data['quantity'],
        d_method_id=d_method_id
    ).distinct().order_by("d_type").values("d_type")
    types_list = []
    for d in d_types:
        types_list.append(d["d_type"])

    if len(types_list) == 0:
        send_to_mm_text = "Unfortunately, this product is out of stock\.\n"
        await send_to_mm(query, user, state, send_to_mm_text)
    else:
        keyboard = await d_type_inline(types_list)
        txt = (f"Country: *{data['country_name']}*\n"
               f"Product type: *{data['type_name']}*\n"
               f"Category: *{data['category_name']}*\n"
               f"Quantity: *{await add_backslash(data['quantity'])}*\n"
               f"Chosen delivery method: *{delivery.name}*\n"
               f"_Now choose the delivery type:_")
        text = await create_m_m_text(user, txt)
        await query.message.edit_caption(
            text,
            parse_mode=types.ParseMode.MARKDOWN_V2,
            reply_markup=keyboard
        )
        delivery = await DeliveryMethod.get_or_none(id=d_method_id)
        await state.update_data(d_method_name=delivery.name)
        await state.update_data(d_method=d_method_id)
        await Market.confirmation.set()


# Delivery type => Order handler
@rate_limit(1, key="market_confirmation")
@dp.callback_query_handler(Regexp(r"d_type:\d+"), state=Market.confirmation)
async def confirmation_callback(query: types.CallbackQuery, state: FSMContext):
    user = await User.get_or_none(tg_id=query.from_user.id)

    d_type_id = int(query.data.split(":")[1])
    await state.update_data(d_type=d_type_id)
    data = await state.get_data()
    d_type_name = (lambda t: {1: "Online", 2: "Express", 3: "Courier"}.get(t, "Preorder"))(d_type_id)
    txt_main = (f"*_Order confirmation:_*\n\n"
                f"Type: *{data['type_name']}*\n"
                f"Product: *{data['category_name']} {await add_backslash(data['quantity'])} \({d_type_name}\)*\n"
                f"Country: *{data['country_name']}*\n"
                f"Delivery method: *{data['d_method_name']}*\n\n")
    stock = await Stock.filter(
        country_id=data["country"],
        type=data['type'],
        category_id=data['category'],
        quantity=data['quantity'],
        d_method_id=data['d_method'],
        d_type=d_type_id
    ).order_by("created_at").first()
    if not stock:
        send_to_mm_text = "Unfortunately, this product is out of stock\.\n"
        await send_to_mm(query, user, state, send_to_mm_text)
    else:
        product = await stock.product
        new_price = product.price
        coupon = 0
        if user.coupon > 0:
            if user.coupon > new_price:
                coupon = user.coupon - (user.coupon - new_price)
                coupon_used = True
                new_price = 0
            else:
                coupon = user.coupon
                coupon_used = True
                new_price -= user.coupon
        else:
            coupon_used = False
        new_price = int(new_price)

        from_balance = 0
        if user.balance >= new_price:
            new_ltc_price = 0.0
            ltc_price = await get_ltc_price_async(product.price)
            ltc_price = math.ceil(ltc_price * 1000) / 1000
            ltc_price_backslash = await add_backslash(ltc_price)
            new_balance = user.balance - new_price
            from_balance = int(user.balance - new_balance)

            if coupon_used:
                txt_before = (f"_Price: *${product.price}* _\(\~*`{ltc_price_backslash}`* LTC\)\n"
                              f"\(_including balance_ ${user.balance} _and coupons_ ${user.coupon}\)\n\n")
            else:
                txt_before = (f"_Price: *${product.price}* _\(\~*`{ltc_price_backslash}`* LTC\)\n"
                              f"\(_including balance_ ${user.balance}\)\n\n")
            txt_after = (f"➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
                         f"_*Balance is enough for purchase\!*_\n\n"
                         f"➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
                         f"To cancel the order click _cancel_\.\n"
                         f"To buy the product click _confirm_\.\n\n"
                         f"*After confirmation the product price will be deducted from the balance \(\-${from_balance}\)\.*\n\n"
                         f"➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
                         f"_*Confirm order?*_")
            txt_main = txt_main + txt_before + txt_after
        else:
            new_usd_price = int(new_price - user.balance)
            new_ltc_price = await get_ltc_price_async(new_usd_price)
            new_ltc_price = new_ltc_price + (new_ltc_price * 0.02)
            new_ltc_price = math.ceil(new_ltc_price * 1000) / 1000
            new_ltc_price_backslash = await add_backslash(new_ltc_price)
            txt_before = (f"Price: *${product.price}*\n\n"
                          f"➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
                          f"_*Total:*_ *`{new_ltc_price_backslash}`* LTC \(${new_usd_price}\)\n")
            if user.balance <= 0 and coupon_used:
                txt_mid = (f"\(_including coupons_ \(${user.coupon}\)\)\n\n"
                           f"➖➖➖➖➖➖➖➖➖➖➖➖\n\n")
            elif user.balance <= 0 and not coupon_used:
                txt_mid = f"\n➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
            elif user.balance > 0 and coupon_used:
                from_balance = user.balance
                txt_mid = (f"\(_including balance_ \(${user.balance}\) _and coupons_ \(${user.coupon}\)\)\n\n"
                           f"➖➖➖➖➖➖➖➖➖➖➖➖\n\n")
            else:
                from_balance = user.balance
                txt_mid = (f"\(_including balance_ \(${user.balance}\)\)\n\n"
                           f"➖➖➖➖➖➖➖➖➖➖➖➖\n\n")
            txt_after = (f"Attention\! After confirmation, LTC wallet for payment will be sent\n"
                         f"You will need to *transfer the exact amount* \(the one in the _*total*_ field\) to the wallet from the details\n\n"
                         f"After confirmation, 30 minutes will be allocated for payment, after the order will be deleted\!\n\n"
                         f"➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
                         f"_*Confirm order?*_")
            txt_main = txt_main + txt_before + txt_mid + txt_after

        await state.update_data(from_balance=from_balance)
        await state.update_data(price_ltc=new_ltc_price)
        await state.update_data(from_coupon=coupon)

        msg_new = await query.message.edit_caption(
            txt_main,
            parse_mode=types.ParseMode.MARKDOWN_V2,
            reply_markup=yes_no
        )

    await Market.balance.set()
    if stock:
        await asyncio.sleep(300)
        if "Confirm order?" in msg_new.caption:
            await msg_new.delete()
            await send_to_mm(query, user, state, "")

# Order creation and pending payment
@rate_limit(1, key="market_yes_no")
@dp.callback_query_handler(Regexp(r"confirmation:yes"), state=Market.balance)
async def yes_no_callback(query: types.CallbackQuery, state: FSMContext):
    user = await User.get_or_none(tg_id=query.from_user.id)
    data = await state.get_data()
    price_ltc = data["price_ltc"]
    price_ltc_backslash = await add_backslash(price_ltc)

    stock = await Stock.filter(
        country_id=data["country"],
        type=data["type"],
        category_id=data["category"],
        quantity=data["quantity"],
        d_method_id=data["d_method"],
        d_type=data["d_type"]
    ).order_by("created_at").first()
    if not stock:
        send_to_mm_text = "Unfortunately, this product is out of stock\.\n"
        await send_to_mm(query, user, state, send_to_mm_text)
    else:
        product = await stock.product
        if price_ltc <= 0:
            status_name = "Оплачен"
            status = "paid"
            await user.save()
            if product.type:
                text_after = f"Your order has been successfully paid\! \nWait for the product to be sent \(1\-10min\)\. \n\n"
            else:
                text_after = f"Your order has been successfully paid\! \nWait for the product to be sent \(up to 24 hours\)\. \n\n"
            text_after += f"➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
            if data["from_balance"] > 0.0:
                user.balance -= data["from_balance"]
                await user.save()
                text_price = f"Paid with balance: *${data['from_balance']}*\n"
                text_after += text_price
            if data["from_coupon"] > 0:
                user.coupon -= data["from_coupon"]
                await user.save()
                text_price = f"Paid with coupon: *${data['from_coupon']}*\n"
                text_after += text_price

        else:
            status_name = "Pending payment"
            status = "pending_payment"
            text_price = (f"Total: *`{price_ltc_backslash}`* LTC\n"
                          f"To wallet: *`{user.wallet}`*\n\n"
                          f"➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
                          f"Your order has been created and is awaiting payment\.\n")

            if product.type:
                text_type = "The product will be sent automatically after payment is received\.\n\n"
            else:
                text_type = "The order will be processed automatically after payment is received\.\n\n"
            if data['from_balance'] > 0.0 and data["from_coupon"] > 0:
                text_type_after = f"After receiving the payment, *${data['from_balance']}* will be deducted from the balance, from the coupons: ${data['from_coupon']}\.\n"
            elif data['from_balance'] > 0.0 and data["from_coupon"] <= 0:
                text_type_after = f"After receiving the payment, *${data['from_balance']}* will be deducted from the balance\.\n"
            elif data['from_balance'] <= 0.0 and data["from_coupon"] > 0:
                text_type_after = f"After receiving the payment, *${data['from_coupon']}* will be deducted from the coupons\.\n"
            else:
                text_type_after = ""
            text_m_after = (f"➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
                            f"Attention\! 30 minutes are allotted for payment, after order will be deleted\!\n")
            text_after = text_price + text_type_after + text_type + text_m_after
            user.active_order = True
        p_t = product.type
        if p_t == True:
            p_t = 0
        else:
            p_t = 1
        order = await Order.create(
            user=user,
            product=product,
            type=p_t,
            price=price_ltc,
            to_balance=data["from_balance"],
            to_coupon=data["from_coupon"]
        )

        text_main = await create_order_m_text(order, status_name)
        txt = text_main + text_after
        msg = query.message
        await msg.delete()
        if price_ltc <= 0.0:
            msg = await dp.bot.send_message(
                chat_id=user.tg_id,
                text=txt,
                parse_mode=types.ParseMode.MARKDOWN_V2,
            )
            order.message_id = msg.message_id

            await state.finish()
            await Market.balance.set()
        else:
            user.active_order = True
            await user.save()
            keyboard = await order_cancel_inline(order.id)
            msg = await dp.bot.send_message(
                chat_id=user.tg_id,
                text=txt,
                parse_mode=types.ParseMode.MARKDOWN_V2,
                reply_markup=keyboard
            )
            order.message_id = msg.message_id

            await Orders.pending_payment.set()
        if data["type"]:
            stock = await Stock.get(id=stock.id)
            await stock.delete()
        order.status = status
        await order.save()
        await state.reset_data()
