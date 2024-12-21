from models import *

from services import UserService, StatService

from telegram import UpdateHandler, UpdateHandlerConfig
from telegram import NotificationManager

from telegram import AIOgramMessage, AIOgramQuery
from telegram import filters, F, IsAdmin
from telegram import States, FSMContext, StateFilter

from telegram.assets import messages, keyboards


class AdminHandler(UpdateHandler):
    notification_manager: NotificationManager
    stat_service: StatService

    def __init__(
            self,
            config: UpdateHandlerConfig,
            notification_manager: NotificationManager,
            user_service: UserService,
            stat_service: StatService
        ):
        super().__init__(config)
        self.notification_manager = notification_manager
        self.user_service = user_service
        self.stat_service = stat_service
    
    async def on_stats(self, message: AIOgramMessage, state: FSMContext):
        stats = await self.stat_service.get_full_statistics()
        await message.answer(
            text=messages.statistics(stats),
            reply_markup=keyboards.ADMIN_STATS
        )

    # async def ban_reported_card(self, query: AIOgramQuery):
    #     await self.user_service.

    def register_handlers(self):
        self.router.message.register(self.on_stats, filters.Command("stats", "statistics"), IsAdmin())
