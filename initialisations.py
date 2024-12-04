from typing import List

from services import UserService

from telegram import UpdateHandler, UpdateHandlerConfig
from telegram.sections import (
    IdleHandler,
    CardCreationHandler
)
from telegram import NotificationManager
from telegram import F, filters


def init_idle_handler(
        user_service: UserService
    ) -> IdleHandler:
    return IdleHandler(
        UpdateHandlerConfig(
            router_name="idle",
            message_filters=[F.text],
        ),
        user_service=user_service
    )


def init_card_creation_handler(
        notification_manager: NotificationManager,
        user_service: UserService,
    ) -> CardCreationHandler:
    return CardCreationHandler(
        UpdateHandlerConfig(
            router_name="card_creation",
        ),
        notification_manager=notification_manager,
        user_service=user_service
    )


def initialise_handlers() -> List[UpdateHandler]:
    handlers = []

    notification_manager = NotificationManager()
    user_service = UserService()

    handlers.append(init_idle_handler(user_service))
    handlers.append(init_card_creation_handler(notification_manager, user_service))

    return handlers
