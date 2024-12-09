from telegram import AIOgramMessage, filters
from telegram import UpdateHandler, UpdateHandlerConfig
from telegram import FSMContext, States

from telegram.assets import messages, keyboards

from models import User

from services import UserService


class IdleHandler(UpdateHandler):

    user_service: UserService

    def __init__(
            self,
            config: UpdateHandlerConfig,
            user_service: UserService
        ):
        super().__init__(config)
        self.user_service = user_service


    async def on_start(self, message: AIOgramMessage, state: FSMContext, user: User):
        await message.answer(
            text=messages.START,
            reply_markup=keyboards.start_card_creation
        )
        await state.set_state(States.CARD_APPROVE)


    def register_handlers(self):
        self.router.message.register(self.on_start, filters.CommandStart())
