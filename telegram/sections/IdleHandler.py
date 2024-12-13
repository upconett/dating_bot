from telegram import AIOgramMessage, filters
from telegram import UpdateHandler, UpdateHandlerConfig
from telegram import FSMContext, States

from telegram.assets import messages, keyboards

from models import User

from services import UserService, CardService


class IdleHandler(UpdateHandler):

    user_service: UserService
    card_service: CardService

    def __init__(
            self,
            config: UpdateHandlerConfig,
            user_service: UserService,
            card_service: CardService
        ):
        super().__init__(config)
        self.user_service = user_service
        self.card_service = card_service


    async def on_start(self, message: AIOgramMessage, state: FSMContext, user: User):
        if await self.card_service.user_has_card(user):
            await message.answer(
                text=messages.IDLE_MENU,
                reply_markup=keyboards.idle_menu
            )
            await state.set_state(States.IDLE)
        else:
            await message.answer(
                text=messages.START,
                reply_markup=keyboards.start_card_creation
            )
            await state.set_state(States.START)


    def register_handlers(self):
        self.router.message.register(self.on_start, filters.CommandStart())
