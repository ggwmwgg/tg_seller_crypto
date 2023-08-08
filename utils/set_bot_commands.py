from aiogram import types


async def set_default_commands(dp):
    """
    Set default commands for bot
    :param dp: Dispatcher
    :return: None
    """
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Start/Restart bot"),
        types.BotCommand("test", "Add test entries to DB"),
    ])


