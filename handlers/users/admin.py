from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Regexp
from aiogram.types import ContentType

from keyboards import main_menu_adm, back_adm, country_inline, back_method, users_menu_adm
from loader import dp
from states.main_adm import Admin
from utils import user_profile_acp
from utils.bot_funcs import add_backslashes, add_photo
from utils.db_api.models import User, Category, DeliveryMethod, Country, Coupons
from utils.misc import rate_limit


# Admin main menu
@rate_limit(1, key="admin_back")
@dp.callback_query_handler(Regexp(r"adm_back"), state=Admin.country)
@dp.callback_query_handler(Regexp(r"adm_back"), state=Admin.d_method)
@dp.callback_query_handler(Regexp(r"adm_back"), state=Admin.category)
@dp.callback_query_handler(Regexp(r"adm_back"), state=Admin.coupons)
@dp.callback_query_handler(Regexp(r"adm_back"), state=Admin.users)
@dp.callback_query_handler(Regexp(r"adm_back"), state=Admin.main)
async def admin_back_callback(query: types.CallbackQuery, state: FSMContext):
    await query.message.edit_text(
        "*Choose an action:*",
        reply_markup=main_menu_adm,
        parse_mode=types.ParseMode.MARKDOWN_V2
    )
    await Admin.main.set()


# Admin countries menu
@rate_limit(1, key="admin_main")
@dp.callback_query_handler(Regexp(r"countries"), state=Admin.main)
@dp.callback_query_handler(Regexp(r"countries"), state="*")
@dp.callback_query_handler(Regexp(r"country_back"), state=Admin.country)
async def country_callback(query: types.CallbackQuery, state: FSMContext):
    m_user = await User.get_or_none(tg_id=query.from_user.id)
    if m_user.role == "admin":
        countries = await Country.all()
        text = "*Countries list:*\n\n"
        for country in countries:
            text += f"- *_{country.name}_*\n"
        text += "\n_Type a name to add a new country:_"
        text = await add_backslashes(text)

        await query.message.edit_text(
            text,
            reply_markup=back_adm,
            parse_mode=types.ParseMode.MARKDOWN_V2
        )
        msg = query.message
        await state.update_data(message_id=msg.message_id)
        await Admin.country.set()


# Admin country add handler
@rate_limit(1, key="admin_country")
@dp.message_handler(state=Admin.country)
async def add_country_callback(message: types.Message, state: FSMContext):
    country = await Country.get_or_none(name=message.text)
    data = await state.get_data()
    message_id = data.get("message_id")
    if country is None:
        await Country.create(name=message.text)
        text = f"*Country {message.text} successfully added!*\n\nTo add another one type a new name:"
    else:
        text = f"*Country {message.text} already exists!*\n\nPlease type another name:"
    countries = await Country.all()
    txt = "*Countries list:*\n\n"
    for country in countries:
        txt += f"- *_{country.name}_*\n"
    text = txt + "\n" + text
    text = await add_backslashes(text)
    await dp.bot.edit_message_text(
        text,
        message.chat.id,
        message_id,
        reply_markup=back_adm,
        parse_mode=types.ParseMode.MARKDOWN_V2
    )
    await message.delete()


# Admin delivery methods menu
@rate_limit(1, key="admin_d_methods")
@dp.callback_query_handler(Regexp(r"d_methods"), state=Admin.main)
@dp.callback_query_handler(Regexp(r"d_methods"), state="*")
@dp.callback_query_handler(Regexp(r"method_back"), state=Admin.d_city)
async def d_method_callback(query: types.CallbackQuery, state: FSMContext):
    m_user = await User.get_or_none(tg_id=query.from_user.id)
    if m_user.role == "admin":
        d_methods = await DeliveryMethod.all()
        text = "*Delivery methods list:*\n\n"
        for d_method in d_methods:
            country = await d_method.country
            text += f"- *_{d_method.name} ({country.name})_*\n"
        text += "\n_Choose a country to add new delivery method:_"
        text = await add_backslashes(text)

        countries = await Country.all()
        c_list = []
        for country in countries:
            c_list.append((country.id, country.name))
        keyboard = await country_inline(c_list)
        await query.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode=types.ParseMode.MARKDOWN_V2
        )
        msg = query.message
        await state.update_data(message_id=msg.message_id)
        await Admin.d_method.set()


# Admin delivery method add 1 handler
@rate_limit(1, key="admin_d_method")
@dp.callback_query_handler(Regexp(r"adm_d_method:\d+"), state=Admin.d_method)
async def d_method_back_callback(query: types.CallbackQuery, state: FSMContext):
    country_id = int(query.data.split(":")[1])
    d_methods = await DeliveryMethod.filter(country_id=country_id)
    text = "*Delivery methods list:*\n\n"
    for d_method in d_methods:
        country = await d_method.country
        text += f"- *_{d_method.name} ({country.name})_*\n"
    text += "\n_Enter new method name:_"
    text = await add_backslashes(text)
    await query.message.edit_text(
        text,
        reply_markup=back_method,
        parse_mode=types.ParseMode.MARKDOWN_V2
    )
    msg = query.message
    await state.update_data(country_id=country_id, message_id=msg.message_id)
    await Admin.d_city.set()


# Admin delivery method add 2 handler
@rate_limit(1, key="admin_d_city")
@dp.message_handler(state=Admin.d_city)
async def add_d_city_callback(message: types.Message, state: FSMContext):
    data = await state.get_data()
    message_id = data.get("message_id")
    country_id = data.get("country_id")
    d_method = await DeliveryMethod.get_or_none(name=message.text, country_id=country_id)
    if d_method is None:
        await DeliveryMethod.create(name=message.text, country_id=country_id)
        text = f"*Delivery method {message.text} added successfully!*\n\nType new name to add another method:"
    else:
        text = f"*Delivery method {message.text} already exists!*\n\nType another name to add another method:"
    d_methods = await DeliveryMethod.filter(country_id=country_id)
    txt = "*Delivery methods list:*\n\n"
    for d_method in d_methods:
        txt += f"- *_{d_method.name}_*\n"
    text = txt + "\n" + text
    text = await add_backslashes(text)
    await dp.bot.edit_message_text(
        text,
        message.chat.id,
        message_id,
        reply_markup=back_adm,
        parse_mode=types.ParseMode.MARKDOWN_V2
    )


# Admin categories menu
@rate_limit(1, key="admin_category")
@dp.callback_query_handler(Regexp(r"categories"), state=Admin.main)
@dp.callback_query_handler(Regexp(r"categories"), state="*")
async def category_callback(query: types.CallbackQuery, state: FSMContext):
    m_user = await User.get_or_none(tg_id=query.from_user.id)
    if m_user.role == "admin":
        categories = await Category.all()
        text = "*Categories list:*\n\n"
        for category in categories:
            text += f"- *_{category.name}_*\n"
        text += ("\nExample: category\_name,category\_description\n"
                 "_Send new category photo with caption (name,description (separated by comma)) included:_")
        text = await add_backslashes(text)
        await query.message.edit_text(
            text,
            reply_markup=back_adm,
            parse_mode=types.ParseMode.MARKDOWN_V2
        )
        msg = query.message
        await state.update_data(message_id=msg.message_id)
        await Admin.category.set()


# Admin categories add handler
@rate_limit(1, key="admin_category")
@dp.message_handler(content_types=ContentType.PHOTO, state=Admin.category)
async def add_category_callback(message: types.Message, state: FSMContext):
    data = await state.get_data()
    message_id = data.get("message_id")
    if message.content_type == ContentType.PHOTO:
        category_name, description = message.caption.split(",")
        image = await add_photo(message, dp)
        category = await Category.get_or_none(name=category_name)
        if category is None:
            await Category.create(name=category_name, description=description, image=image)
            text = (f"*Category {category_name} added successfully!*\n\n"
                    f"Example: name,description (separated by comma)\n"
                    f"Send next photo with caption to add new category:")
        else:
            text = f"*Category {category_name} already exists!*\n\nSend a photo with another category name,description:"
        categories = await Category.all()
        txt = "*Categories list:*\n\n"
        for category in categories:
            txt += f"- *_{category.name}_*\n"
        text = txt + "\n" + text
        text = await add_backslashes(text)
        await dp.bot.edit_message_text(
            text,
            message.chat.id,
            message_id,
            reply_markup=back_adm,
            parse_mode=types.ParseMode.MARKDOWN_V2
        )
        await message.delete()


# Admin coupons menu
@rate_limit(1, key="admin_coupons")
@dp.callback_query_handler(Regexp(r"coupons"), state=Admin.main)
@dp.callback_query_handler(Regexp(r"coupons"), state="*")
async def coupons_callback(query: types.CallbackQuery, state: FSMContext):
    m_user = await User.get_or_none(tg_id=query.from_user.id)
    if m_user.role == "admin":
        coupons = await Coupons.all()
        text = "*Coupons list (code,amount,№ of usages):*\n\n"
        for coupon in coupons:
            text += f"- *_`{coupon.code}` (${coupon.amount}, {coupon.usages_left})_*\n"
        text += ("\nExample: coupon,1,10 (CODE coupon with AMOUNT of $1 and 10 USAGES)\n"
                 "_Send coupon code, amount and № of usages (separated by comma) to add new one:_")
        text = await add_backslashes(text)
        await query.message.edit_text(
            text,
            reply_markup=back_adm,
            parse_mode=types.ParseMode.MARKDOWN_V2
        )
        msg = query.message
        await state.update_data(message_id=msg.message_id)
        await Admin.coupons.set()


# Admin coupons add handler
@rate_limit(1, key="admin_coupons")
@dp.message_handler(state=Admin.coupons)
async def add_coupons_callback(message: types.Message, state: FSMContext):
    data = await state.get_data()
    message_id = data.get("message_id")
    coupon_name, amount, usages_left = message.text.split(",")
    coupon = await Coupons.get_or_none(code=coupon_name)
    if coupon is None:
        await Coupons.create(code=coupon_name, amount=amount, usages_left=usages_left)
        text = (f"*Coupon `{coupon_name}` added successfully!*\n\n"
                f"Example: coupon,1,10 (CODE coupon with AMOUNT of $1 and 10 USAGES)\n"
                f"_Send another coupon,amount,usages to add:_")
    else:
        text = (f"*Coupon `{coupon_name}` already exists!*\n\n"
                f"Example: coupon,1,10 (CODE coupon with AMOUNT of $1 and 10 USAGES)\n"
                f"_Send another coupon,amount,usages to add:_")
    coupons = await Coupons.all()
    txt = "*Coupons list (code,amount,№ of usages):*\n\n"
    for coupon in coupons:
        txt += f"- *_`{coupon.code}` (${coupon.amount}, {coupon.usages_left})_*\n"
    text = txt + "\n" + text
    text = await add_backslashes(text)
    await dp.bot.edit_message_text(
        text,
        message.chat.id,
        message_id,
        reply_markup=back_adm,
        parse_mode=types.ParseMode.MARKDOWN_V2
    )
    await message.delete()


# Admin users menu
@rate_limit(1, key="admin_users")
@dp.callback_query_handler(Regexp(r"users"), state=Admin.main)
@dp.callback_query_handler(Regexp(r"users"), state="*")
async def users_callback(query: types.CallbackQuery, state: FSMContext):
    m_user = await User.get_or_none(tg_id=query.from_user.id)
    if m_user.role == "admin":
        users = await User.all()
        text = "*Users list:*\n\n"
        for user in users:
            text += f"- *_`@{user.username}`_*\n"
        text += "\nExample: @username\n_Send username:_"
        text = await add_backslashes(text)
        await query.message.edit_text(
            text,
            reply_markup=back_adm,
            parse_mode=types.ParseMode.MARKDOWN_V2
        )
        msg = query.message
        await state.update_data(message_id=msg.message_id)
        await Admin.users.set()


# Admin select user handler
@rate_limit(1, key="admin_users_back")
@dp.callback_query_handler(Regexp(r"adm_back"), state=Admin.users_deposit)
@dp.callback_query_handler(Regexp(r"adm_back"), state=Admin.users_coupon)
@dp.callback_query_handler(Regexp(r"adm_back"), state=Admin.users_role)
async def back_callback(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("user_id")
    user = await User.get(id=user_id)
    text = await user_profile_acp(user, f"\nChoose an action:")
    keyboard = await users_menu_adm(user)
    await Admin.users.set()
    await query.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode=types.ParseMode.MARKDOWN_V2
    )


# Admin selected user actions menu
@rate_limit(1, key="admin_users")
@dp.message_handler(state=Admin.users)
async def add_users_callback(message: types.Message, state: FSMContext):
    data = await state.get_data()
    message_id = data.get("message_id")
    username = message.text[1:]
    user = await User.get_or_none(username=username)
    if user is None:
        users = await User.all()
        text = "*Users list:*\n\n"
        for u in users:
            text += f"- *_`@{u.username}`_*\n"
        text += f"\n*User `@{username}` not found!*\n\nExample: @username\n_Type correct username:_"
        text = await add_backslashes(text)
        keyboard = back_adm
    else:
        await state.update_data(user_id=user.id)
        text = await user_profile_acp(user)
        keyboard = await users_menu_adm(user)
    await dp.bot.edit_message_text(
        text,
        message.chat.id,
        message_id,
        reply_markup=keyboard,
        parse_mode=types.ParseMode.MARKDOWN_V2
    )
    await message.delete()


# Admin user deposit handler
@rate_limit(1, key="admin_user_deposit")
@dp.callback_query_handler(Regexp(r"adm_add_balance:\d+"), state=Admin.users)
async def add_balance_callback(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    message_id = data.get("message_id")
    user_id = int(query.data.split(":")[1])
    user = await User.get(id=user_id)
    text = await user_profile_acp(user, "Type amount in $:")
    keyboard = back_adm
    await dp.bot.edit_message_text(
        text,
        query.message.chat.id,
        message_id,
        reply_markup=keyboard,
        parse_mode=types.ParseMode.MARKDOWN_V2
    )
    await state.update_data(user_id=user_id)
    await Admin.users_deposit.set()


# Admin user (after deposit) menu
@rate_limit(1, key="admin_user_deposit")
@dp.message_handler(state=Admin.users_deposit)
async def add_balance_callback_m(message: types.Message, state: FSMContext):
    data = await state.get_data()
    message_id = data.get("message_id")
    user_id = data.get("user_id")
    user = await User.get(id=user_id)
    amount = message.text
    if amount.isdigit():
        user.balance += int(amount)
        await user.save()
        text = await user_profile_acp(user, f"_Balance topped up by ${amount}!_\nChoose an action:")
        keyboard = await users_menu_adm(user)
        await Admin.users.set()
    else:
        text = await user_profile_acp(user, "Type correct amount in $:")
        keyboard = back_adm
    await dp.bot.edit_message_text(
        text,
        message.chat.id,
        message_id,
        reply_markup=keyboard,
        parse_mode=types.ParseMode.MARKDOWN_V2
    )
    await message.delete()


# Admin user coupon handler
@rate_limit(1, key="admin_user_coupon")
@dp.callback_query_handler(Regexp(r"adm_add_coupon:\d+"), state=Admin.users)
async def add_coupon_callback(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    message_id = data.get("message_id")
    user_id = int(query.data.split(":")[1])
    user = await User.get(id=user_id)
    text = await user_profile_acp(user, "Type coupon amount in $:")
    keyboard = back_adm
    await dp.bot.edit_message_text(
        text,
        query.message.chat.id,
        message_id,
        reply_markup=keyboard,
        parse_mode=types.ParseMode.MARKDOWN_V2
    )
    await state.update_data(user_id=user_id)
    await Admin.users_coupon.set()


# Admin user (after coupon) menu
@rate_limit(1, key="admin_user_deposit")
@dp.message_handler(state=Admin.users_coupon)
async def add_coupon_callback_m(message: types.Message, state: FSMContext):
    data = await state.get_data()
    message_id = data.get("message_id")
    user_id = data.get("user_id")
    user = await User.get(id=user_id)
    amount = message.text
    if amount.isdigit():
        user.coupon += int(amount)
        await user.save()
        text = await user_profile_acp(user, f"_${amount} coupon issued!_\nChoose an action:")
        keyboard = await users_menu_adm(user)
        await Admin.users.set()
    else:
        text = await user_profile_acp(user, "Enter correct amount in $:")
        keyboard = back_adm
    await dp.bot.edit_message_text(
        text,
        message.chat.id,
        message_id,
        reply_markup=keyboard,
        parse_mode=types.ParseMode.MARKDOWN_V2
    )
    await message.delete()


# Admin user change role handler
@rate_limit(1, key="admin_users_change_role")
@dp.callback_query_handler(Regexp(r"adm_change_role:\d+"), state=Admin.users)
async def change_role_callback(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    message_id = data.get("message_id")
    user_id = int(query.data.split(":")[1])
    user = await User.get(id=user_id)
    text = await user_profile_acp(user, "Type a new role:")
    await dp.bot.edit_message_text(
        text,
        query.message.chat.id,
        message_id,
        reply_markup=back_adm,
        parse_mode=types.ParseMode.MARKDOWN_V2
    )
    await state.update_data(user_id=user_id)
    await Admin.users_role.set()


# Admin user (after change role) menu
@rate_limit(1, key="admin_users_change_role")
@dp.message_handler(state=Admin.users_role)
async def change_role_callback_m(message: types.Message, state: FSMContext):
    data = await state.get_data()
    message_id = data.get("message_id")
    user_id = data.get("user_id")
    user = await User.get(id=user_id)
    role = message.text
    user.role = role
    await user.save()
    text = await user_profile_acp(user, f"_User role changed to {role}!_\nChoose an action:")
    keyboard = await users_menu_adm(user)
    await Admin.users.set()
    await dp.bot.edit_message_text(
        text,
        message.chat.id,
        message_id,
        reply_markup=keyboard,
        parse_mode=types.ParseMode.MARKDOWN_V2
    )


# Admin user ban/unban handler
@rate_limit(1, key="admin_users_ban")
@dp.callback_query_handler(Regexp(r"adm_ban:\d+"), state=Admin.users)
@dp.callback_query_handler(Regexp(r"adm_unban:\d+"), state=Admin.users)
async def ban_user_callback(query: types.CallbackQuery, state: FSMContext):
    user_id = int(query.data.split(":")[1])
    user = await User.get(id=user_id)
    if user.banned:
        user.banned = False
        text = await user_profile_acp(user, "_User unbanned!_\nChoose an action:")
    else:
        user.banned = True
        text = await user_profile_acp(user, "_User banned!_\nChoose an action:")
    await user.save()
    keyboard = await users_menu_adm(user)
    await Admin.users.set()
    await dp.bot.edit_message_text(
        text,
        query.message.chat.id,
        query.message.message_id,
        reply_markup=keyboard,
        parse_mode=types.ParseMode.MARKDOWN_V2
    )
