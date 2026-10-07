import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from Configs.config_reader import get_config, BotConfig
from handlers.general import router
from Configs.DBConfig import TABLES
from handlers.general import base

dp = Dispatcher()
dp.include_router(router)


async def main():
    bot_config = get_config(model=BotConfig, root_key='bot')
    bot = Bot(bot_config.token.get_secret_value())
    await base.init(TABLES)
    await dp.start_polling(bot)
    

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
