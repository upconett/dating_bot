from typing import List

from controllers import DBController, CacheController
from controllers.database import SQLiteController
from controllers.cache import DictCacheController

from logic.realisations.card import DefaultCardWriter, DefaultCardLoader
from logic.realisations.user import DefaultUserLoader, DefaultUserWriter

from services import UserService, CardService

from telegram import UpdateHandler, UpdateHandlerConfig
from telegram.sections import (
    IdleHandler,
    CardCreationHandler,
    SettingsHandler,
    RecomendationHandler
)
from telegram import NotificationManager
from telegram import F, filters
from telegram.utils.middleware import MediaGroupMiddleware, DefaultMiddleware


def init_idle_handler(
        user_service: UserService,
        card_service: CardService
    ) -> IdleHandler:
    return IdleHandler(
        UpdateHandlerConfig(
            router_name="idle",
            message_filters=[F.text],
            message_middleware=DefaultMiddleware(user_service),
        ),
        user_service=user_service,
        card_service=card_service
    )


def init_card_creation_handler(
        user_service: UserService,
        card_service: CardService
    ) -> CardCreationHandler:
    return CardCreationHandler(
        UpdateHandlerConfig(
            router_name="card_creation",
            message_middleware=MediaGroupMiddleware(user_service),
        ),
        user_service=user_service,
        card_service=card_service
    )


def init_settings_handler(
        user_service: UserService,
    ) -> SettingsHandler:
    return SettingsHandler(
        UpdateHandlerConfig(
            router_name="settings",
            message_middleware=DefaultMiddleware(user_service),
        ),
        user_service=user_service,
    )


def initialise_user_service(db_controller: DBController, cache_controller: CacheController) -> UserService:
    user_loader = DefaultUserLoader(db_controller, cache_controller)
    user_writer = DefaultUserWriter(db_controller, cache_controller)

    return UserService(
        user_loader=user_loader,
        user_writer=user_writer,
    )


def initialise_card_service(db_controller: DBController, cache_controller: CacheController) -> CacheController:
    card_writer = DefaultCardWriter(db_controller, cache_controller)
    card_loader = DefaultCardLoader(db_controller, cache_controller) # TODO : implement card_loader
    # card_validator = DefaultCardValidator() # TODO : implement card_validator

    return CardService(
        card_writer=card_writer, # TODO : implement card_loader, card_validator
        card_loader=card_loader
    )


def init_recomendation_handler(
        user_service: UserService,
        card_service: CardService
    ) -> RecomendationHandler:
    return RecomendationHandler(
        UpdateHandlerConfig(
            router_name="recomendations",
            message_middleware=DefaultMiddleware(user_service),
        ),
        user_service=user_service,
        card_service=card_service
    )



def initialise_handlers() -> List[UpdateHandler]:
    handlers = []

    db_controller = SQLiteController("test.db")
    cache_controller = DictCacheController()

    notification_manager = NotificationManager()
    user_service = initialise_user_service(db_controller, cache_controller)
    card_service = initialise_card_service(db_controller, cache_controller)

    handlers.append(init_idle_handler(user_service, card_service))
    handlers.append(init_card_creation_handler(user_service, card_service))
    handlers.append(init_settings_handler(user_service))
    handlers.append(init_recomendation_handler(user_service, card_service))

    return handlers
