from typing import List

from telegram import AIOgramFilter


class UpdateHandlerConfig():
    router_name: str
    message_filters: List[AIOgramFilter]
    callback_filters: List[AIOgramFilter]

    def __init__(
            self,
            router_name: str, 
            message_filters: List[AIOgramFilter] = [],
            callback_filters: List[AIOgramFilter] = []
        ):
        self.router_name = router_name
        self.message_filters = message_filters
        self.callback_filters = callback_filters
