import asyncio

from telegram import Config
from telegram import AIOgramBot, AIOgramDispatcher, DefaultBotProperties
from telegram import MasterHandler


from initialisations import master_handler, stat_service


async def main():
    await stat_service.start_stats_cycle()
    await master_handler.run()


if __name__ == "__main__":
    asyncio.run(main())
