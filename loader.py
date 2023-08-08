from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from data import config

# Here we create bot object and dispatcher object with MemoryStorage
bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = RedisStorage2(config.REDIS_HOST, config.REDIS_PORT, password=config.REDIS_PASSWORD)

dp = Dispatcher(bot, storage=storage)

__all__ = ["bot", "storage", "dp"]
