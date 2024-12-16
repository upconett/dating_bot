from models import User

from services import UserService, CardService

from telegram import AIOgramMessage, AIOgramQuery, filters, F
from telegram import UpdateHandler, UpdateHandlerConfig
from telegram import FSMContext, States, StateFilter

from telegram import NotificationManager
from telegram.assets import messages, keyboards

from telegram.utils.card import *


class IdleHandler(UpdateHandler):

    notification_manager: NotificationManager
    user_service: UserService
    card_service: CardService

    def __init__(
            self,
            config: UpdateHandlerConfig,
            notification_manager: NotificationManager,
            user_service: UserService,
            card_service: CardService
        ):
        super().__init__(config)
        self.notification_manager = notification_manager
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

        
    async def my_card(self, message: AIOgramMessage, state: FSMContext, user: User):
        await state.set_state(States.CARD_MENU)
        card = await self.card_service.get_by_user(user)
        await message.answer(
            text=messages.YOUR_CARD,
            reply_markup=keyboards.card_menu
        )
        await send_card(message, card, keyboards.card_menu)


    async def response_like(self, query: AIOgramQuery, state: FSMContext, user: User):
        like_sender_id = int(query.data.split("_")[2])
        like_sender = await self.user_service.get_by_tg_id(like_sender_id)
        await self.notification_manager.send_response_like(user, like_sender)
        await query.message.edit_caption(
            caption=query.message.caption
            + messages.link_to_user(like_sender),
            reply_markup=None,
            parse_mode="HTML",
        )
        await query.answer()

    
    async def response_dislike(self, query: AIOgramQuery, state: FSMContext, user: User):
        await query.message.edit_reply_markup(reply_markup=None)
        await query.answer()


    def register_handlers(self):
        self.router.message.register(self.on_start, filters.CommandStart())
        self.router.message.register(self.my_card, F.text == "Моя анкета", StateFilter(States.IDLE))
        self.router.callback_query.register(self.response_like, F.data.startswith("response_like_"))
        self.router.callback_query.register(self.response_dislike, F.data.startswith("response_dislike_"))
