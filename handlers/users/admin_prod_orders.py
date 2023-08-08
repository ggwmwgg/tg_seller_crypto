import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Regexp
from aiogram.types import ContentType

from data.config import admins
from keyboards import back_adm, preorder_adm, orders_del_adm, preorder_back, preorders_adm, order_adm, order_back
from loader import dp
from states.main_adm import Admin
from utils import add_backslash
from utils.bot_funcs import create_order_m_text, add_backslashes, get_stocks, cat_method_country, get_preorders_list, \
    create_order_b_text, add_photo, create_product_stock
from utils.db_api.models import User, Stock, Order, Product
from utils.misc import rate_limit


# Admin send preorders handler
@rate_limit(1, 'admin_order_send')
@dp.callback_query_handler(Regexp(r"order_send:\d+"), state=Admin.main)
@dp.callback_query_handler(Regexp(r"order_send_a:\d+"), state="*")
async def admin_order_send_callback(query: types.CallbackQuery, state: FSMContext):
    m_user = await User.get(id=query.from_user.id)
    if m_user.role == "admin":
        order_id = query.data.split(":")[1]
        query_name = query.data.split(":")[0]
        order = await Order.get(id=order_id)
        txt = f"Send a photo of the product with its description in caption for order *{order.id}*\."
        await state.update_data(
            msg_id=query.message.message_id,
            order_id=order_id
        )
        if query_name == "order_send_a":
            await query.message.edit_text(
                txt,
                parse_mode=types.ParseMode.MARKDOWN_V2,
                reply_markup=back_adm
            )
        else:
            await dp.bot.send_message(
                query.from_user.id,
                txt,
                parse_mode=types.ParseMode.MARKDOWN_V2,
                reply_markup=back_adm
            )
        await Admin.order_send.set()


# Admin send preorders handler last step
@rate_limit(0, 'admin_order_send_msg')
@dp.message_handler(state=Admin.order_send, content_types=ContentType.PHOTO)
async def admin_order_send_msg_callback(message: types.Message, state: FSMContext):
    data = await state.get_data()
    order_id = data.get("order_id")
    msg_id = data.get("msg_id")
    order = await Order.get(id=order_id)
    user = await order.user
    capt = message.caption
    if capt is not None:
        capt = await add_backslashes(capt)
    else:
        capt = ""
    adm_text = await create_order_b_text(order, user)
    txt = "*Payed*\n\n"
    if order.to_balance > 0:
        txt = txt + f"From balance: *`${order.to_balance}`*\n"
    if order.to_coupon > 0:
        txt = txt + f"From coupon: *`${order.to_coupon}`*\n"
    if order.price > 0.0:
        txt = txt + f"From LTC: *`{await add_backslash(order.price)}`*\n"
    balance_txt = txt + "\n➖➖➖➖➖➖➖➖➖➖➖➖\n\n"

    text = await create_order_m_text(order, "Delivered")
    description = (f"Description: _{capt}_\n\n"
                   f"➖➖➖➖➖➖➖➖➖➖➖➖\n\n")
    user_txt = (f"*Thank you for your purchase\!*\n_If you have any questions, contact support\._\n\n"
                f"*Return to main menu by pressing _/start_*")
    user_txt = text + description + balance_txt + user_txt
    adm_text = text + description + balance_txt + adm_text

    await dp.bot.delete_message(message.chat.id, msg_id)
    await dp.bot.delete_message(user.tg_id, order.message_id)

    for admin in admins:
        await dp.bot.send_photo(
            admin,
            message.photo[-1].file_id,
            caption=adm_text,
            parse_mode=types.ParseMode.MARKDOWN_V2
        )

    await dp.bot.send_photo(
        user.tg_id,
        message.photo[-1].file_id,
        caption=user_txt,
        parse_mode=types.ParseMode.MARKDOWN_V2
    )

    await order.delete()
    await message.delete()


# Admin add product handler
@rate_limit(1, 'admin_order_add')
@dp.callback_query_handler(Regexp(r"orders_add"), state=Admin.main)
async def admin_order_add_callback(query: types.CallbackQuery, state: FSMContext):
    new_txt = ("To add new product send photo or group of photos with following information on first photo caption:\n\n"
               "product type (1.Online 2.Express 3.Courier),quantity,category_id,country_id,delivery_method_id,price,description\n"
               "For example: 1,1,1,1,1,25,Description\n")
    text = await cat_method_country()
    txt = await get_stocks(True, new_txt)
    text = text + "\n\n" + txt
    msg = query.message
    await state.update_data(message_id=msg.message_id)
    await query.message.edit_text(
        text,
        reply_markup=order_back,
        parse_mode=types.ParseMode.MARKDOWN_V2
    )
    await Admin.order_add.set()


# Admin add product handler second step
@rate_limit(0, 'admin_order_add_final')
@dp.message_handler(state=Admin.order_add, content_types=ContentType.PHOTO)
async def admin_order_add_final_callback(message: types.Message, state: FSMContext):
    data = await state.get_data()
    m_g_id = data.get("m_g_id")
    if message.media_group_id is not None:
        if m_g_id == message.media_group_id:
            await asyncio.sleep(5)
            data = await state.get_data()
            product = await Product.get(id=data["p_id"])
            image = await add_photo(message, dp)
            await product.images.add(image)
            await message.delete()
        else:
            await state.update_data(m_g_id=message.media_group_id)
            product = await create_product_stock(message)
            await state.update_data(p_id=product.id)
            image = await add_photo(message, dp)
            await product.images.add(image)
    else:
        split = message.caption.split(",")
        if len(split) == 7:
            product = await create_product_stock(message)
            image = await add_photo(message, dp)
            await product.images.add(image)
        else:
            product = None
    if message.media_group_id is None or message.media_group_id != m_g_id:
        await message.delete()
        txt = await get_stocks(True, f"*Product {product.id} added successfully!*\n_Choose an action:_")
        await dp.bot.edit_message_text(
            text=txt,
            chat_id=message.chat.id,
            message_id=data["message_id"],
            reply_markup=order_adm,
            parse_mode=types.ParseMode.MARKDOWN_V2
        )
        await Admin.main.set()


# Admin preorders list handler
@rate_limit(1, 'admin_preorders_list')
@dp.callback_query_handler(Regexp(r"preorders_list"), state=Admin.main)
@dp.callback_query_handler(Regexp(r"adm_back"), state=Admin.order_send)
async def admin_preorders_list_callback(query: types.CallbackQuery):
    text = await get_preorders_list()
    keyboard = await preorders_adm()
    await query.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode=types.ParseMode.MARKDOWN_V2
    )
    await Admin.main.set()


# Admin preorders add handler
@rate_limit(1, 'admin_preorder_add')
@dp.callback_query_handler(Regexp(r"preorder_add"), state=Admin.main)
async def admin_preorder_add_callback(query: types.CallbackQuery, state: FSMContext):
    new_txt = ("\nTo add a new product send following text (separated by comma) in format:\n\n"
               "product type (1.Online 2.Express 3.Courier), quantity,category id,country id,delivery method id,price(w/o $),description\n"
               "For example: 1,1,1,1,1,25,Example description\n")
    text = await cat_method_country()
    txt = await get_stocks(False, new_txt)
    text = text + "\n\n" + txt
    msg = query.message
    await state.update_data(message_id=msg.message_id)
    await query.message.edit_text(
        text,
        reply_markup=preorder_back,
        parse_mode=types.ParseMode.MARKDOWN_V2
    )
    await Admin.preorder_add.set()


# Admin prods to delete list handler
@rate_limit(1, 'admin_order_del')
@dp.callback_query_handler(Regexp(r"orders_del"), state=Admin.main)
async def admin_back_callback(query: types.CallbackQuery):
    txt = await get_stocks(True, "\nChoose a product to remove (id):")
    keyboard = await orders_del_adm(True)
    await query.message.edit_text(
        txt,
        reply_markup=keyboard,
        parse_mode=types.ParseMode.MARKDOWN_V2
    )


# Admin prods delete handler last step
@rate_limit(1, 'admin_order_del')
@dp.callback_query_handler(Regexp(r"order_del:\d+"), state=Admin.main)
async def admin_preorder_del_callback(query: types.CallbackQuery):
    stock_id = int(query.data.split(":")[1])
    stock = await Stock.get(id=stock_id)
    product = await stock.product
    images = await product.images.all()
    for image in images:
        await image.delete()
    await stock.delete()
    await product.delete()
    txt = await get_stocks(True, f"Product {stock_id} removed\n\nChoose next product to remove (id):")
    keyboard = await orders_del_adm(True)
    await query.message.edit_text(
        txt,
        reply_markup=keyboard,
        parse_mode=types.ParseMode.MARKDOWN_V2
    )


# Admin digital orders list handler
@dp.callback_query_handler(Regexp(r"order_back"), state=Admin.main)
@dp.callback_query_handler(Regexp(r"order_back"), state=Admin.order_add)
@dp.callback_query_handler(Regexp(r"digital"), state=Admin.main)
@dp.callback_query_handler(Regexp(r"digital"), state="*")
async def admin_mom_callback(query: types.CallbackQuery):
    m_user = await User.get_or_none(tg_id=query.from_user.id)
    if m_user.role == "admin":
        txt = await get_stocks(True)
        await query.message.edit_text(
            txt,
            reply_markup=order_adm,
            parse_mode=types.ParseMode.MARKDOWN_V2
        )
        await Admin.main.set()


# Admin preorders to delete list handler
@rate_limit(1, 'admin_preorder_del')
@dp.callback_query_handler(Regexp(r"preorder_del"), state=Admin.main)
async def admin_back_callback(query: types.CallbackQuery):
    txt = await get_stocks(False, "\nChoose a product to remove (id):")
    keyboard = await orders_del_adm()
    await query.message.edit_text(
        txt,
        reply_markup=keyboard,
        parse_mode=types.ParseMode.MARKDOWN_V2
    )


# Admin preorders list (actions) handler
@rate_limit(1, 'admin_preorder')
@dp.callback_query_handler(Regexp(r"preorder_back"), state=Admin.main)
@dp.callback_query_handler(Regexp(r"preorder_back"), state=Admin.preorder_add)
@dp.callback_query_handler(Regexp(r"preorder"), state=Admin.main)
@dp.callback_query_handler(Regexp(r"preorder"), state="*")
async def admin_preorder_callback(query: types.CallbackQuery):
    m_user = await User.get_or_none(tg_id=query.from_user.id)
    if m_user.role == "admin":
        txt = await get_stocks(False)
        await query.message.edit_text(
            txt,
            reply_markup=preorder_adm,
            parse_mode=types.ParseMode.MARKDOWN_V2
        )
        await Admin.main.set()


# Admin preorders delete handler last step
@rate_limit(1, 'admin_preorder_del')
@dp.callback_query_handler(Regexp(r"pre_del:\d+"), state=Admin.main)
async def admin_preorder_del_callback(query: types.CallbackQuery):
    stock_id = int(query.data.split(":")[1])
    stock = await Stock.get(id=stock_id)
    product = await stock.product
    await stock.delete()
    await product.delete()
    txt = await get_stocks(False, f"Product {stock_id} removed\n\nSelect next product to remove (id):")
    keyboard = await orders_del_adm()
    await query.message.edit_text(
        txt,
        reply_markup=keyboard,
        parse_mode=types.ParseMode.MARKDOWN_V2
    )


# Admin preorder products add handler
@rate_limit(1, 'admin_preorder_add')
@dp.message_handler(state=Admin.preorder_add, content_types=ContentType.TEXT)
async def admin_preorder_add_final(message: types.Message, state: FSMContext):
    data = await state.get_data()
    split = message.text.split(",")
    if len(split) == 7:
        p = await create_product_stock(message, False)
        txt = await get_stocks(False, f"*\n\nProduct {p.id} added!*\n_Choose an action:_")
        await Admin.main.set()
        await dp.bot.edit_message_text(
            txt,
            chat_id=message.chat.id,
            message_id=data['message_id'],
            reply_markup=preorder_adm,
            parse_mode=types.ParseMode.MARKDOWN_V2
        )
    await message.delete()
