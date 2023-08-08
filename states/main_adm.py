from aiogram.dispatcher.filters.state import StatesGroup, State


class Admin(StatesGroup):
    main = State()
    country = State()
    d_method = State()
    d_city = State()
    category = State()
    coupons = State()
    users = State()
    users_deposit = State()
    users_coupon = State()
    users_role = State()
    preorder_add = State()
    order_add = State()
    order_send = State()
