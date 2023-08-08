from aiogram.dispatcher.filters.state import StatesGroup, State


class Main(StatesGroup):
    main = State()
    market = State()
    deposit = State()
    coupon = State()
    rules = State()
    showcase = State()


class Market(StatesGroup):
    category = State()
    quantity = State()
    d_method = State()
    d_type = State()
    confirmation = State()
    balance = State()


class Orders(StatesGroup):
    pending_payment = State()
