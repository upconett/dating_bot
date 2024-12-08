from typing import List
from telegram import AIOgramRouter, AIOgramFilter, BaseMiddleware

from abc import ABC, abstractmethod
from telegram import UpdateHandlerConfig


class UpdateHandler(ABC):
    router: AIOgramRouter

    def __init__(self, config: UpdateHandlerConfig):
        self.router=AIOgramRouter(name=config.router_name)
        self.router.message.middleware(config.message_middleware)
        self.__assign_filters(
            config.message_filters,
            config.callback_filters
        )


    def __assign_filters(
            self,
            message_filters: List[AIOgramFilter],
            callback_filters: List[AIOgramFilter],
        ):
        self.router.message.filter(*message_filters)
        self.router.callback_query.filter(*callback_filters)


    @abstractmethod
    def register_handlers(self):
        ...
