import asyncio

from telegram import Config
from telegram import AIOgramBot, AIOgramDispatcher
from telegram import MasterHandler


from initialisations import initialise_handlers


async def main():
    config = Config(".env")

    bot = AIOgramBot(token=config.token)
    dispatcher = AIOgramDispatcher()

    update_handlers = initialise_handlers()

    master_handler = MasterHandler(
        bot=bot,
        dispatcher=dispatcher,
        update_handlers=update_handlers
    )

    await master_handler.run()


if __name__ == "__main__":
    asyncio.run(main())
