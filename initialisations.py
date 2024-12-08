from typing import List

from controllers.database import SQLiteController
from controllers.cache import DictCacheController

from logic.realisations.card import DefaultCardWriter

from services import UserService, CardService

from telegram import UpdateHandler, UpdateHandlerConfig
from telegram.sections import (
    IdleHandler,
    CardCreationHandler
)
from telegram import NotificationManager
from telegram import F, filters
from telegram.utils.middleware import MediaGroupMiddleware


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
        card_service: CardService
    ) -> CardCreationHandler:
    return CardCreationHandler(
        UpdateHandlerConfig(
            router_name="card_creation",
            message_middleware=MediaGroupMiddleware()
        ),
        notification_manager=notification_manager,
        user_service=user_service,
        card_service=card_service
    )


def initialise_handlers() -> List[UpdateHandler]:
    handlers = []

    db_controller = SQLiteController("test.db")
    cache_controller = DictCacheController()

    notification_manager = NotificationManager()
    user_service = UserService()

    card_writer = DefaultCardWriter(
        db_controller=db_controller,
        cache_controller=cache_controller
    )
    card_service = CardService(card_writer)

    handlers.append(init_idle_handler(user_service))
    handlers.append(init_card_creation_handler(
        notification_manager,
        user_service,
        card_service
    ))

    return handlers
