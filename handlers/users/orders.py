from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Regexp

from loader import dp
from states.main import Orders
from utils.bot_funcs import create_order_m_text
from utils.db_api.models import User, Stock, Order
from utils.misc import rate_limit


# Order cancel handler
@rate_limit(1, key="market_yes_no")
@dp.callback_query_handler(Regexp(r"order_cancel:\d+"), state=Orders.pending_payment)
async def yes_no_callback(query: types.CallbackQuery, state: FSMContext):
    user = await User.get_or_none(tg_id=query.from_user.id)
    order_id = int(query.data.split(":")[1])
    order = await Order.get_or_none(id=order_id)
    if order.type != 2:
        product = await order.product

    if order.status != "paid":
        if order.type == 0:
            await Stock.create(
                product=product,
                country=await product.country,
                type=product.type,
                category=await product.category,
                d_method=await product.d_method,
                d_type=product.d_type,
                quantity=product.quantity
            )
            user.false_orders += 1
        text_main = await create_order_m_text(order, "Cancelled")
        text_main += f"Order cancelled\. Back to menu /start"
        user.active_order = False
        await user.save()
        await order.delete()
    else:
        text_main = await create_order_m_text(order, "Paid")
        text_main += "Order already paid and processing\."

    await state.finish()
    await query.message.edit_reply_markup()
    await query.message.edit_text(
        text_main,
        parse_mode=types.ParseMode.MARKDOWN_V2,
    )
