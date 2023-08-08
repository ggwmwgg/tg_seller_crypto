from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware

from data.config import admins
from utils import generate_wallet_async
from utils.db_api.models import User


# Ban check middleware
class WatcherMiddleware(BaseMiddleware):
    allowed_updates = ["callback_query", "message"]

    async def trigger(self, action, arg):
        obj, *args, data = arg

        if not any(
                update in action for update in self.allowed_updates
        ):
            return

        if not action.startswith("process_"):
            return
        handler = current_handler.get()
        if not handler:
            return

        allow = getattr(handler, "allow", False)
        if allow:
            return

        user_id = await User.get_or_none(tg_id=obj.from_user.id)
        if not user_id:
            wallet = await generate_wallet_async()
            await User.create(
                tg_id=obj.from_user.id,
                username=obj.from_user.username,
                full_name=obj.from_user.full_name,
                wallet=wallet["address"],
                seed=wallet["mnemonic"]
            )
        elif user_id.banned and user_id.tg_id in admins:
            user_id.banned = False
            user_id.role = "admin"
            await user_id.save()
            await obj.answer("You were unbanned (auto middle | super admin)")
        elif user_id.banned:
            await obj.answer("You are banned")
            raise CancelHandler()
        elif user_id.role == "user" and user_id.tg_id in admins:
            user_id.role = "admin"
            await user_id.save()
            await obj.answer("You are admin now (auto middle | super admin)")
        else:
            if user_id.username != obj.from_user.username:
                user_id.username = obj.from_user.username
                await user_id.save()
            elif user_id.full_name != obj.from_user.full_name:
                user_id.full_name = obj.from_user.full_name
                await user_id.save()
            elif user_id.false_orders >= 5:
                user_id.banned = True
                await user_id.save()
