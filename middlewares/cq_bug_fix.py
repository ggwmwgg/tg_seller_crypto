from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware


class CQBugFix(BaseMiddleware):
    async def on_pre_process_callback_query(self, cq: types.CallbackQuery, data: dict):
        await cq.answer()
