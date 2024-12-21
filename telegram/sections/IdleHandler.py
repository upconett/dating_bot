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
            card = await self.card_service.get_by_user(user)
            await message.answer(
                text=messages.IDLE_MENU,
                reply_markup=keyboards.idle_menu(card)
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

    
    async def disable_card_begin(self, message: AIOgramMessage, state: FSMContext, user: User):
        await state.set_state(States.ENSURE_DISABLING)
        await message.answer(
            text=messages.ENSURE_DISABLING,
            reply_markup=keyboards.are_you_sure
        )

    async def disable_card_end(self, message: AIOgramMessage, state: FSMContext, user: User):
        await state.set_state(States.IDLE)
        card = await self.card_service.get_by_user(user)
        card = await self.card_service.disable_card(card)
        await message.answer(messages.CARD_DISABLED)
        await message.answer(
            text=messages.IDLE_MENU,
            reply_markup=keyboards.idle_menu(card)
        )

   
    async def enable_card_begin(self, message: AIOgramMessage, state: FSMContext, user: User):
        await state.set_state(States.ENSURE_ENABLING)
        await message.answer(
            text=messages.ENSURE_ENABLING,
            reply_markup=keyboards.are_you_sure
        )

    async def enable_card_end(self, message: AIOgramMessage, state: FSMContext, user: User):
        await state.set_state(States.IDLE)
        card = await self.card_service.get_by_user(user)
        card = await self.card_service.enable_card(card)
        await message.answer(messages.CARD_ENABLED)
        await message.answer(
            text=messages.IDLE_MENU,
            reply_markup=keyboards.idle_menu(card)
        )

    async def i_am_not_sure(self, message: AIOgramMessage, state: FSMContext, user: User):
        await state.set_state(States.IDLE)
        card = await self.card_service.get_by_user(user)
        await message.answer(
            text=messages.IDLE_MENU,
            reply_markup=keyboards.idle_menu(card)
        )


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


    async def report(self, query: AIOgramQuery, state: FSMContext, user: User):
        reported_card_id = int(query.data.split("_")[1])
        await query.message.edit_reply_markup(reply_markup=None)
        await query.message.answer(messages.REPORT_SENT)
        await self.notification_manager.report(user, reported_card_id)


    def register_handlers(self):
        self.router.message.register(self.on_start, filters.CommandStart())
        self.router.message.register(self.my_card, F.text == "Моя анкета", StateFilter(States.IDLE))

        self.router.message.register(self.disable_card_begin, F.text == "Отключить анкету", StateFilter(States.IDLE))
        self.router.message.register(self.disable_card_end, F.text == "Да", StateFilter(States.ENSURE_DISABLING))

        self.router.message.register(self.enable_card_begin, F.text == "Включить анкету", StateFilter(States.IDLE))
        self.router.message.register(self.enable_card_end, F.text == "Да", StateFilter(States.ENSURE_ENABLING))

        self.router.message.register(self.i_am_not_sure, F.text == "Нет", StateFilter(States.ENSURE_DISABLING, States.ENSURE_ENABLING))

        self.router.callback_query.register(self.response_like, F.data.startswith("response_like_"))
        self.router.callback_query.register(self.response_dislike, F.data.startswith("response_dislike_"))
        self.router.callback_query.register(self.report, F.data.startswith("report_"))
