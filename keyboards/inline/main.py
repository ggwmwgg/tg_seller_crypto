from aiogram import types
from utils.db_api.models import Country

yes_no = types.InlineKeyboardMarkup()
yes_no.add(types.InlineKeyboardButton("Confirm", callback_data="confirmation:yes"))
yes_no.add(types.InlineKeyboardButton("Cancel", callback_data="confirmation:no"))

back = types.InlineKeyboardMarkup()
back.add(types.InlineKeyboardButton("Back", callback_data="main:back"))


async def type_inline(type_s: list) -> types.InlineKeyboardMarkup:  # True online False preorder
    k_s = types.InlineKeyboardMarkup()
    for t_id in type_s:
        callback_id = f"type:{t_id}"
        if t_id:
            k_s.add(types.InlineKeyboardButton("Digital", callback_data=callback_id))
        else:
            k_s.add(types.InlineKeyboardButton("Preorder", callback_data=callback_id))
    k_s.add(types.InlineKeyboardButton("Back", callback_data="main:back"))
    return k_s


async def m_m_inline() -> types.InlineKeyboardMarkup:
    countries = await Country.filter(stocks__isnull=False).distinct().order_by("-name").values("id", "name")
    c_list = []
    for country in countries:
        c_list.append((country["id"], country["name"]))
    markup = types.InlineKeyboardMarkup()
    for c_id, country in c_list:
        markup.add(types.InlineKeyboardButton(country, callback_data=f"country:{c_id}"))
    markup.add(types.InlineKeyboardButton("Showcase", callback_data="showcase"))
    markup.row(
        types.InlineKeyboardButton("Deposit", callback_data="deposit"),
        types.InlineKeyboardButton("Coupon", callback_data="coupon_add"),
    )
    markup.row(
        types.InlineKeyboardButton("Rules", callback_data="rules"),
        types.InlineKeyboardButton("Support", url="https://t.me/UserLinkExample"),  # https://t.me/mrShelby_9
    )
    markup.add(types.InlineKeyboardButton("Reviews chat", url="https://t.me/ChatLinkExample"))
    return markup


async def categories_inline(categories: list) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    for c_id, category in categories:
        markup.add(types.InlineKeyboardButton(category, callback_data=f"category:{c_id}"))
    markup.add(types.InlineKeyboardButton("Back", callback_data="category:back"))
    return markup


async def quantity_inline(quantity: list) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    for q in quantity:
        callback_id = f"quantity:{q}"
        markup.add(types.InlineKeyboardButton(q, callback_data=callback_id))
    markup.add(types.InlineKeyboardButton("Back", callback_data="quantity:back"))
    return markup


async def d_method_inline(d_method: list) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    for d_id, d_method in d_method:
        callback_id = f"d_method:{d_id}"
        markup.add(types.InlineKeyboardButton(d_method, callback_data=callback_id))
    markup.add(types.InlineKeyboardButton("Back", callback_data="d_method:back"))
    return markup


async def d_type_inline(type_d: list) -> types.InlineKeyboardMarkup:  # 1. Regular(m) 2. Express(t) 3. Courier(p) 4. Pickup(pre)
    k_d = types.InlineKeyboardMarkup()
    for t_id in type_d:
        callback_id = f"d_type:{t_id}"
        if t_id == 0:
            k_d.add(types.InlineKeyboardButton("Online", callback_data=callback_id))
        elif t_id == 1:
            k_d.add(types.InlineKeyboardButton("Express", callback_data=callback_id))
        elif t_id == 2:
            k_d.add(types.InlineKeyboardButton("Courier", callback_data=callback_id))
        else:
            k_d.add(types.InlineKeyboardButton("Preorder", callback_data=callback_id))
    k_d.add(types.InlineKeyboardButton("Back", callback_data="d_type:back"))
    return k_d


async def order_cancel_inline(order_id) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Cancel order", callback_data=f"order_cancel:{order_id}"))
    return markup


async def send_order_inline(order_id) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Send order", callback_data=f"order_send:{order_id}"))
    return markup
