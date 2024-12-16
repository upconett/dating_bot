from typing import List

from telegram import AIOgramMessage, StateFilter, F
from telegram import InputMediaPhoto, InputMediaVideo
from telegram import UpdateHandler, UpdateHandlerConfig
from telegram import FSMContext, States

from telegram.assets import messages, keyboards
from telegram import NotificationManager

from models import User, Card, Media

from services import UserService, CardService
from logic.exceptions import CardNotFound


class RecomendationHandler(UpdateHandler):
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


    async def recomend_first(self, message: AIOgramMessage, state: FSMContext, user: User):
        await message.answer(
            text="Загрузка анкет...",
            reply_markup=keyboards.recomended_card
        )
        await self._send_next_recomendation(message, state, user)
    
    async def dislike_card(self, message: AIOgramMessage, state: FSMContext, user: User):
        await self._send_next_recomendation(message, state, user)

    async def go_idle(self, message: AIOgramMessage, state: FSMContext, user: User):
        await state.set_state(States.IDLE)
        await message.answer(
            text=messages.IDLE_MENU,
            reply_markup=keyboards.idle_menu
        )

    async def like_card(self, message: AIOgramMessage, state: FSMContext, user: User):
        data = await state.get_data()
        last_card = data.get("last_card")
        await self._send_next_recomendation(message, state, user)
        receiver = await self.user_service.get_by_card(last_card)
        await self.notification_manager.send_like(user, receiver)
    

    async def start_message_card(self, message: AIOgramMessage, state: FSMContext, user: User):
        data = await state.get_data()
        last_card = data.get("last_card")
        await message.answer(
            text=messages.message_card(last_card),
            reply_markup=keyboards.empty
        )
        await state.set_state(States.MESSAGE_CARD)

    
    async def send_message_card(self, message: AIOgramMessage, state: FSMContext, user: User):
        data = await state.get_data()
        last_card = data.get("last_card")
        await state.set_state(States.RECOMENDATIONS)
        await message.answer(
            text=messages.MESSAGE_SENT,
            reply_markup=keyboards.recomended_card
        )
        await self._send_next_recomendation(message, state, user)
        receiver = await self.user_service.get_by_card(last_card)
        await self.notification_manager.send_message(user, receiver, message.text)


    #region private

    async def _send_next_recomendation(self, message: AIOgramMessage, state: FSMContext, user: User) -> AIOgramMessage:
        try:
            card = await self.card_service.get_recomended(user)
            await state.set_state(States.RECOMENDATIONS)
            await state.set_data({"last_card": card})
            return await self._send_card(message, card)
        except CardNotFound:
            await self.card_service.update_recomendations(user)
            await message.answer(
                text="Анкеты для вас закончились :(\nПодождите пока мы подберем новые...",
                reply_markup=keyboards.recomended_card
            )
        try:
            card = await self.card_service.get_recomended(user)
            await state.set_state(States.RECOMENDATIONS)
            await state.set_data({"last_card": card})
            return await self._send_card(message, card)
        except CardNotFound:
            return await message.answer(
                text="К сожалению, анкеты не найдены...\nПопробуйте позже",
                reply_markup=keyboards.recomended_card
            )


    async def _send_card(self, message: AIOgramMessage, card: Card) -> AIOgramMessage:
        if len(card.media) == 0:
            return await self._send_card_without_media(message, card)
        elif len(card.media) == 1:
            return await self._send_card_with_single_media(message, card)
        elif len(card.media) > 1:
            return await self._send_card_with_media_group(message, card)

    
    async def _send_card_without_media(self, message: AIOgramMessage, card: Card) -> AIOgramMessage:
        return await message.answer(
            text=messages.card_info(card),
            reply_markup=keyboards.recomended_card,
            parse_mode='HTML',
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
                    reply_markup=keyboard,
                    parse_mode='HTML',
                )
            case "video":
                return await message.answer_video(
                    video=media.file_id,
                    caption=caption,
                    reply_markup=keyboard,
                    parse_mode='HTML',
                )
            case _:
                return None


    def register_handlers(self):
        self.router.message.register(self.recomend_first, F.text == "/test")
        self.router.message.register(self.recomend_first, F.text == "Смотреть анкеты", StateFilter(States.IDLE))
        self.router.message.register(self.recomend_first, F.text == "Начать общаться!", StateFilter(States.TO_RECOMENDATIONS))
        self.router.message.register(self.dislike_card, F.text == "💔", StateFilter(States.RECOMENDATIONS))
        self.router.message.register(self.like_card, F.text == "❤️", StateFilter(States.RECOMENDATIONS))
        self.router.message.register(self.go_idle, F.text == "💤", StateFilter(States.RECOMENDATIONS))
        self.router.message.register(self.start_message_card, F.text == "💬", StateFilter(States.RECOMENDATIONS))
        self.router.message.register(self.send_message_card, F.text, StateFilter(States.MESSAGE_CARD))
