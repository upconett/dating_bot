from typing import List

from controllers import DBController, CacheController
from controllers.database import SQLiteController
from controllers.cache import DictCacheController

from logic import CardLoader
from logic.realisations.card import DefaultCardWriter, DefaultCardLoader
from logic.realisations.user import DefaultUserLoader, DefaultUserWriter

from services import (
    UserService,
    CardService,
    StatService,
    PaymentService
)

from telegram import AIOgramBot
from telegram import UpdateHandler, UpdateHandlerConfig
from telegram.sections import (
    IdleHandler,
    CardCreationHandler,
    SettingsHandler,
    RecomendationHandler,
    CardMenuHandler,
    AdminHandler,
    PaymentHandler,
)
from telegram import NotificationManager
from telegram import F, filters
from telegram.utils.middleware import MediaGroupMiddleware, DefaultMiddleware

from telegram import Config
from telegram import AIOgramBot, AIOgramDispatcher, DefaultBotProperties
from telegram import MasterHandler

#region Config

config = Config(".env")

#endregion

#region Controllers

db_controller = SQLiteController("test.db")
cache_controller = DictCacheController()

#endregion


#region Logic

user_loader = DefaultUserLoader(db_controller, cache_controller)
user_writer = DefaultUserWriter(db_controller, cache_controller)

card_writer = DefaultCardWriter(db_controller, cache_controller)
card_loader = DefaultCardLoader(db_controller, cache_controller)

#endregion


#region Services

user_service = UserService(
        user_loader=user_loader,
        user_writer=user_writer,
)

card_service = CardService(
    card_writer=card_writer,
    card_loader=card_loader,
)

stat_service = StatService(
    user_loader=user_loader,
    user_writer=user_writer,
    card_loader=card_loader,
)

payment_service = PaymentService(
    config=config,
)

#endregion


#region Bot

bot = AIOgramBot(
    token=config.token,
    default=DefaultBotProperties(
        parse_mode="HTML"
    )
)

dispatcher = AIOgramDispatcher()

notification_manager = NotificationManager(bot, card_loader)

#endregion


#region Handlers

idle_handler = IdleHandler(
    UpdateHandlerConfig(
        router_name="idle",
        message_filters=[F.text],
        message_middleware=DefaultMiddleware(user_service),
    ),
    notification_manager=notification_manager,
    user_service=user_service,
    card_service=card_service
)

card_creation_handler = CardCreationHandler(
    UpdateHandlerConfig(
        router_name="card_creation",
        message_middleware=MediaGroupMiddleware(user_service),
    ),
    user_service=user_service,
    card_service=card_service
)

settings_handler = SettingsHandler(
    UpdateHandlerConfig(
        router_name="settings",
        message_middleware=DefaultMiddleware(user_service),
    ),
    user_service=user_service,
    card_service=card_service,
)

recomendation_handler = RecomendationHandler(
    UpdateHandlerConfig(
        router_name="recomendations",
        message_middleware=DefaultMiddleware(user_service),
    ),
    notification_manager=notification_manager,
    user_service=user_service,
    card_service=card_service,
    stat_service=stat_service,
)

card_menu_handler = CardMenuHandler(
    UpdateHandlerConfig(
        router_name="card_menu",
        message_middleware=MediaGroupMiddleware(user_service),
    ),
    user_service=user_service,
    card_service=card_service,
)

admin_handler = AdminHandler(
    UpdateHandlerConfig(
        router_name="admin",
        message_middleware=DefaultMiddleware(user_service),
    ),
    notification_manager=notification_manager,
    user_service=user_service,
    stat_service=stat_service,
)

payment_handler = PaymentHandler(
    UpdateHandlerConfig(
        router_name="payment",
        message_middleware=DefaultMiddleware(user_service)
    ),
    notification_manager=notification_manager,
    user_service=user_service,
    stat_service=stat_service,
    payment_service=payment_service
)

#endregion


#region MasterHandler

master_handler = MasterHandler(
    bot=bot,
    dispatcher=dispatcher,
    update_handlers=[
        idle_handler,
        card_creation_handler,
        settings_handler,
        recomendation_handler,
        card_menu_handler,
        admin_handler,
        payment_handler,
    ]
)

#endregion
