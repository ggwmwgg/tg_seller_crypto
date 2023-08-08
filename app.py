import asyncio

from aiogram import executor
from tortoise import Tortoise

from loader import dp
from utils.notifier import notify_admins
from utils.orders_checker import check_pending_payments, check_paid_orders, withdrawn_orders_checker
from utils.set_bot_commands import set_default_commands
from utils.db_api import init_db
import middlewares, handlers  # Don't delete this line, it's necessary for handlers and middlewares to work


async def on_startup(dp):
    """
    What to do on startup

    Creating connection to DB, setting default bot commands,
    notifying admins about bot start and starting orders checkers.

    :param dp: Dispatcher
    :return: None
    """

    await init_db()
    await notify_admins(dp)
    await set_default_commands(dp)
    asyncio.create_task(check_pending_payments(dp))
    asyncio.create_task(check_paid_orders(dp))
    asyncio.create_task(withdrawn_orders_checker(dp))

async def on_shutdown(dp):
    """
    What to do on shutdown

    Closing connection to DB and storage.

    :param dp: Dispatcher
    :return: None
    """
    await Tortoise.close_connections()
    await dp.storage.close()


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
