import os
from dotenv import load_dotenv

load_dotenv()

# Bot Super Admins
ads = str(os.getenv("ADMINS")).split(',')
admins = []
for ad in ads:
    admins.append(int(ad))

# Database config
BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
POSTGRES_USER = str(os.getenv("POSTGRES_USER"))
POSTGRES_PASSWORD = str(os.getenv("POSTGRES_PASSWORD"))
POSTGRES_DATABASE = str(os.getenv("POSTGRES_DB"))
POSTGRES_HOST = str(os.getenv("POSTGRES_HOST"))
POSTGRES_PORT = str(os.getenv("POSTGRES_PORT"))
POSTGRES_URI = f"postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"

# Tortoise ORM config
TORTOISE_CONFIG = {
    "connections": {"default": POSTGRES_URI},
    "apps": {
        "models": {
            "models": ["utils.db_api.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}

# Redis config
REDIS_HOST = str(os.getenv("REDIS_HOST"))
REDIS_PORT = str(os.getenv("REDIS_PORT"))
REDIS_PASSWORD = str(os.getenv("REDIS_PASSWORD"))

# Database encryption key
MAIN_PW = str(os.getenv("MAIN_PW"))

# Withdrawal wallet
WALLET = str(os.getenv("WALLET"))

# Timezone
TIMEZONE = 5  # UTC+5


# Создать уведомление об ошибке
# добавить трай эксепт и если эксепт то отправить уведомление об ошибке
# Поменять примеры товаров категорий и сделать докер, редис и ридми
