from typing import List

from telegram import AIOgramMessage, StateFilter, F
from telegram import InputMediaPhoto, InputMediaVideo
from telegram import UpdateHandler, UpdateHandlerConfig
from telegram import FSMContext, States

from telegram.assets import messages, keyboards

from models import User, Card, Media

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
            await self._send_card(message, card)
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
            await self._send_card(message, card)
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
            await self._send_card(message, card)
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
            await self._send_card(message, card)
        except CardNotFound:
            await message.answer(
                text="К сожалению, анкеты не найдены...\nПопробуйте позже",
                reply_markup=keyboards.recomended_card
            )
            return


    async def go_idle(self, message: AIOgramMessage, state: FSMContext, user: User):
        await message.answer(
            text=messages.IDLE_MENU,
            reply_markup=keyboards.idle_menu
        )
        await state.set_state(States.IDLE)

    
    async def _send_card(self, message: AIOgramMessage, card: Card):
        if len(card.media) == 0:
            return await self._send_card_without_media(message, card)
        elif len(card.media) == 1:
            return await self._send_card_with_single_media(message, card)
        elif len(card.media) > 1:
            return await self._send_card_with_media_group(message, card)

    
    async def _send_card_without_media(self, message: AIOgramMessage, card: Card) -> AIOgramMessage:
        return await message.answer(
            text=messages.card_info(card),
            reply_markup=keyboards.recomended_card
        )

    async def _send_card_with_media_group(self, message: AIOgramMessage, card: Card) -> AIOgramMessage:
        media_group: List[InputMediaPhoto|InputMediaVideo] = []
        for m in card.media:
            if m.type == "photo": media_group.append(InputMediaPhoto(media=m.file_id))
            if m.type == "video": media_group.append(InputMediaVideo(media=m.file_id))
        media_group[0].caption = messages.card_info(card)
        return await message.answer_media_group(media_group)


    async def _send_card_with_single_media(self, message: AIOgramMessage, card: Card) -> AIOgramMessage:
        media = card.media[0]
        caption = messages.card_info(card)
        keyboard = keyboards.recomended_card
        match(media.type):
            case "photo":
                return await message.answer_photo(
                    photo=media.file_id,
                    caption=caption,
                    reply_markup=keyboard
                )
            case "video":
                return await message.answer_video(
                    video=media.file_id,
                    caption=caption,
                    reply_markup=keyboard
                )
            case _:
                return None


    def register_handlers(self):
        self.router.message.register(self.recomend_first, F.text == "/test")
        self.router.message.register(self.recomend_first, F.text == "Смотреть анкеты", StateFilter(States.IDLE))
        self.router.message.register(self.recomend_first, F.text == "Начать общаться!", StateFilter(States.TO_RECOMENDATIONS))
        self.router.message.register(self.dislike_card, F.text == "💔", StateFilter(States.RECOMENDATIONS))
        self.router.message.register(self.go_idle, F.text == "💤", StateFilter(States.RECOMENDATIONS))

