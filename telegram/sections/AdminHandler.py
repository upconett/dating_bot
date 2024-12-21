from models import *

from services import UserService, CardService, StatService

from telegram import UpdateHandler, UpdateHandlerConfig
from telegram import NotificationManager

from telegram import AIOgramMessage, AIOgramQuery
from telegram import filters, F, IsAdmin
from telegram import States, FSMContext, StateFilter

from telegram.assets import messages, keyboards


class AdminHandler(UpdateHandler):
    notification_manager: NotificationManager
    user_service: UserService
    card_service: CardService
    stat_service: StatService

    def __init__(
            self,
            config: UpdateHandlerConfig,
            notification_manager: NotificationManager,
            user_service: UserService,
            card_service: CardService,
            stat_service: StatService,
        ):
        super().__init__(config)
        self.notification_manager = notification_manager
        self.user_service = user_service
        self.card_service = card_service
        self.stat_service = stat_service
    
    async def on_stats(self, message: AIOgramMessage, state: FSMContext):
        stats = await self.stat_service.get_full_statistics()
        await message.answer(
            text=messages.statistics(stats),
            reply_markup=keyboards.ADMIN_STATS
        )

    async def ban_reported_card(self, query: AIOgramQuery):
        tg_id = int(query.data.split("_")[1])
        user = await self.user_service.get_by_tg_id(tg_id)
        card = await self.card_service.get_by_user(user)
        await self.user_service.ban_user(user)
        await self.card_service.disable_card(card)
        await query.message.edit_reply_markup(reply_markup=None)
        await query.message.answer(
            f"Пользователь {user.first_name} ({user.username}) был забанен" # TODO : Move to messages
        )
    
    async def spare_reported_card(self, query: AIOgramQuery):
        await query.message.reply_to_message.delete()
        await query.message.delete()


    def register_handlers(self):
        self.router.message.register(self.on_stats, filters.Command("stats", "statistics"), IsAdmin())
        self.router.callback_query.register(self.ban_reported_card, F.data.startswith("ban_"), IsAdmin())
        self.router.callback_query.register(self.spare_reported_card, F.data == "spare", IsAdmin())
