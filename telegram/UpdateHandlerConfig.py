from typing import List

from telegram import AIOgramFilter, BaseMiddleware


class UpdateHandlerConfig():
    router_name: str
    message_filters: List[AIOgramFilter]
    callback_filters: List[AIOgramFilter]
    message_middleware: BaseMiddleware
    query_middleware: BaseMiddleware

    def __init__(
            self,
            router_name: str, 
            message_filters: List[AIOgramFilter] = [],
            callback_filters: List[AIOgramFilter] = [],
            message_middleware: BaseMiddleware = None,
            query_middleware: BaseMiddleware = None,
        ):
        self.router_name = router_name
        self.message_filters = message_filters
        self.callback_filters = callback_filters
        self.message_middleware = message_middleware
        self.query_middleware = query_middleware
