from telegram import AIOgramMessage, StateFilter, F
from telegram import UpdateHandler, UpdateHandlerConfig
from telegram import FSMContext, States

from telegram.assets import messages, keyboards

from models import User

from services import UserService, CardService
from logic.exceptions import CardNotFound


class RecomendationHandler(UpdateHandler):
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


    async def recomend_first(self, message: AIOgramMessage, state: FSMContext, user: User):
        try:
            card = await self.card_service.get_recomended(user)
            await message.answer(
                text=messages.card_info(card),
                reply_markup=keyboards.recomended_card
            )
            await state.set_state(States.RECOMENDATIONS)
            return
        except CardNotFound:
            await message.answer(
                text="Анкеты для вас закончились :(\nПодождите пока мы подберем новые...",
                reply_markup=keyboards.empty
            )
            await self.card_service.update_recomendations(user)

        try:
            card = await self.card_service.get_recomended(user)
            await message.answer(
                text=messages.card_info(card),
                reply_markup=keyboards.recomended_card
            )
            await state.set_state(States.RECOMENDATIONS)
        except CardNotFound:
            await message.answer(
                text="К сожалению, анкеты не найдены...\nПопробуйте позже",
                reply_markup=keyboards.recomended_card
            )
            return

    
    async def dislike_card(self, message: AIOgramMessage, state: FSMContext, user: User):
        try:
            card = await self.card_service.get_recomended(user)
            await message.answer(
                text=messages.card_info(card),
                reply_markup=keyboards.recomended_card
            )
            await state.set_state(States.RECOMENDATIONS)
            return
        except CardNotFound:
            await message.answer(
                text="Анкеты для вас закончились :(\nПодождите пока мы подберем новые...",
                reply_markup=keyboards.empty
            )
            await self.card_service.update_recomendations(user)

        try:
            card = await self.card_service.get_recomended(user)
            await message.answer(
                text=messages.card_info(card),
                reply_markup=keyboards.recomended_card
            )
        except CardNotFound:
            await message.answer(
                text="К сожалению, анкеты не найдены...\nПопробуйте позже",
                reply_markup=keyboards.recomended_card
            )
            return



    def register_handlers(self):
        self.router.message.register(self.recomend_first, F.text == "/test")
        self.router.message.register(self.dislike_card, F.text == "💔", StateFilter(States.RECOMENDATIONS))

