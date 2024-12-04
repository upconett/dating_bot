from typing import List

from telegram import AIOgramBot, AIOgramDispatcher

from telegram import UpdateHandler


class MasterHandler():
    bot: AIOgramBot
    dispatcher: AIOgramDispatcher


    def __init__(
            self,
            bot: AIOgramBot,
            dispatcher: AIOgramDispatcher,
            update_handlers: List[UpdateHandler]
        ):
        self.bot = bot
        self.dispatcher = dispatcher
        self.__register_handler_functions(update_handlers)
        self.__include_update_handlers(update_handlers)


    def __register_handler_functions(self, update_handlers: List[UpdateHandler]):
        for update_handler in update_handlers:
            update_handler.register_handlers()


    def __include_update_handlers(self, update_handlers: List[UpdateHandler]):
        for update_handler in update_handlers:
            self.dispatcher.include_router(update_handler.router)


    async def run(self):
        await self.bot.delete_webhook(True)
        print("Bot started!")
        await self.dispatcher.start_polling(self.bot)
