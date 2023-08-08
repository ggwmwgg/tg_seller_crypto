from aiogram import types
from utils.db_api.models import User, Stock, Order

main_menu_adm = types.InlineKeyboardMarkup()
main_menu_adm.add(types.InlineKeyboardButton("Users", callback_data="users"))
main_menu_adm.row(
   types.InlineKeyboardButton("Digital", callback_data="digital"),
   types.InlineKeyboardButton("Preorders", callback_data="preorder")
)
main_menu_adm.row(
    types.InlineKeyboardButton("Countries", callback_data="countries"),
    types.InlineKeyboardButton("Delivery methods", callback_data="d_methods")
)
main_menu_adm.row(
    types.InlineKeyboardButton("Categories", callback_data="categories"),
    types.InlineKeyboardButton("Coupons", callback_data="coupons")
)


back_adm = types.InlineKeyboardMarkup()
back_adm.add(types.InlineKeyboardButton("Back", callback_data="adm_back"))


back_method = types.InlineKeyboardMarkup()
back_method.add(types.InlineKeyboardButton("Back", callback_data="method_back"))

cat_back = types.InlineKeyboardMarkup()
cat_back.add(types.InlineKeyboardButton("Back", callback_data="cat_back"))

preorder_adm = types.InlineKeyboardMarkup()
preorder_adm.add(types.InlineKeyboardButton("Add", callback_data="preorder_add"))
preorder_adm.add(types.InlineKeyboardButton("Delete", callback_data="preorder_del"))
preorder_adm.add(types.InlineKeyboardButton("Active orders", callback_data="preorders_list"))
preorder_adm.add(types.InlineKeyboardButton("Back", callback_data="adm_back"))

preorder_back = types.InlineKeyboardMarkup()
preorder_back.add(types.InlineKeyboardButton("Back", callback_data="preorder_back"))

order_adm = types.InlineKeyboardMarkup()
order_adm.add(types.InlineKeyboardButton("Add", callback_data="orders_add"))
order_adm.add(types.InlineKeyboardButton("Delete", callback_data="orders_del"))
order_adm.add(types.InlineKeyboardButton("Back", callback_data="adm_back"))

order_back = types.InlineKeyboardMarkup()
order_back.add(types.InlineKeyboardButton("Back", callback_data="order_back"))


async def country_inline(countries: list) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    for c_id, country in countries:
        markup.add(types.InlineKeyboardButton(country, callback_data=f"adm_d_method:{c_id}"))
    markup.add(types.InlineKeyboardButton("Back", callback_data="adm_back"))
    return markup


async def users_menu_adm(user: User) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Deposit", callback_data=f"adm_add_balance:{user.id}"))
    markup.add(types.InlineKeyboardButton("Add coupon", callback_data=f"adm_add_coupon:{user.id}"))
    markup.add(types.InlineKeyboardButton("Change role", callback_data=f"adm_change_role:{user.id}"))
    if not user.banned:
        markup.add(types.InlineKeyboardButton("Ban", callback_data=f"adm_ban:{user.id}"))
    else:
        markup.add(types.InlineKeyboardButton("Unban", callback_data=f"adm_unban:{user.id}"))
    markup.add(types.InlineKeyboardButton("Back", callback_data="adm_back"))
    return markup


async def orders_del_adm(type_s: bool = False) -> types.InlineKeyboardMarkup:
    stocks = await Stock.filter(
        type=type_s
    ).all()

    markup = types.InlineKeyboardMarkup()
    for stock in stocks:
        if type_s:
            markup.add(types.InlineKeyboardButton(stock.id, callback_data=f"order_del:{stock.id}"))
        else:
            markup.add(types.InlineKeyboardButton(stock.id, callback_data=f"pre_del:{stock.id}"))
    if type_s:
        markup.add(types.InlineKeyboardButton("Back", callback_data="order_back"))
    else:
        markup.add(types.InlineKeyboardButton("Back", callback_data="preorder_back"))
    return markup


async def preorders_adm() -> types.InlineKeyboardMarkup:
    orders = await Order.filter(
        status="delivery",
        type=1
    )
    markup = types.InlineKeyboardMarkup()
    for order in orders:
        markup.add(types.InlineKeyboardButton(f"Send {order.id}", callback_data=f"order_send_a:{order.id}"))
    markup.add(types.InlineKeyboardButton("Back", callback_data="preorder_back"))
    return markup




