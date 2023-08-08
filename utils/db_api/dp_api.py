import logging
from tortoise import Tortoise
from data.config import TORTOISE_CONFIG


# DB API
async def init_db():
    logging.info("Connecting to DB")
    await Tortoise.init(config=TORTOISE_CONFIG)
    logging.info("Connected to DB")

    logging.info("Creating tables")
    await Tortoise.generate_schemas()
    logging.info("Tables created")
