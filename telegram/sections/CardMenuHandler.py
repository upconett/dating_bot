from models import User, Media, Card

from services import UserService, CardService

from telegram import AIOgramMessage, AIOgramQuery, filters, F
from telegram import UpdateHandler, UpdateHandlerConfig
from telegram import FSMContext, States, StateFilter
from telegram import ContentType as CT

from telegram import NotificationManager
from telegram.assets import messages, keyboards

from telegram.utils.card import *
from telegram.utils.exceptions import InvalidMedia, TooManyMedia


class CardMenuHandler(UpdateHandler):

    notification_manager: NotificationManager
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


    async def go_back(self, message: AIOgramMessage, state: FSMContext, user: User):
        await state.set_state(States.IDLE)
        card = await self.card_service.get_by_user(user)
        await message.answer(
            text=messages.IDLE_MENU,
            reply_markup=keyboards.idle_menu(card)
        )

    async def change_media_start(self, message: AIOgramMessage, state: FSMContext, user: User):
        await state.set_state(States.CHANGE_MEDIA)
        await message.answer(
            text=messages.CHANGE_MEDIA,
            reply_markup=keyboards.CHANGE_MEDIA
        )
    
    async def change_media_cancel(self, message: AIOgramMessage, state: FSMContext, user: User):
        await state.set_state(States.CARD_MENU)
        card = await self.card_service.get_by_user(user)
        await message.answer(
            text=messages.YOUR_CARD,
            reply_markup=keyboards.card_menu
        )
        await send_card(message, card, keyboards.card_menu)


    async def change_media_handle(self, message: AIOgramMessage, state: FSMContext, media_group: List[AIOgramMessage], user: User):
        try:
            new_media = await self._extract_media(message, media_group, state)
            card = await self.card_service.get_by_user(user)
            card.media = new_media
            await self.card_service.update_card(card)
            await state.set_state(States.CARD_MENU)
            await message.answer(
                text=messages.YOUR_CARD,
                reply_markup=keyboards.card_menu
            )
            await send_card(message, card, keyboards.card_menu)
        except InvalidMedia:
            await message.answer(messages.INVALID_MEDIA)
        except TooManyMedia:
            await message.answer(messages.TOO_MANY_MEDIA)
        
    
    async def recreate_card_name(self, message: AIOgramMessage, state: FSMContext):
        await self._empty_state_data(state)
        await message.answer(messages.REQUEST_NAME, reply_markup=keyboards.empty)
        await state.set_state(States.REQUEST_NAME)

        
    async def _extract_media(self, message: AIOgramMessage, media_group: List[AIOgramMessage], state: FSMContext):
        if media_group is not None:
            return self._collect_media(media_group)
        elif message.content_type in (CT.PHOTO, CT.VIDEO):
            return self._get_photo_or_video(message)
        elif message.content_type == CT.TEXT:
            return []
        else:
            raise InvalidMedia
    
    def _get_photo_or_video(self, message: AIOgramMessage) -> List[Media]:
        if message.photo:
            return [Media("photo", message.photo[-1].file_id)]
        elif message.video:
            return [Media("video", message.video.file_id)]
        else:
            raise InvalidMedia()

    def _collect_media(self, media_group: List[AIOgramMessage]) -> List[Media]:
        media = []
        if len(media_group) > 3: raise TooManyMedia()
        for message in media_group:
            if message.photo:
                media.append(Media("photo", message.photo[-1].file_id))
            elif message.video:
                media.append(Media("video", message.video.file_id))
            else:
                raise InvalidMedia()
        return media

    async def _add_state_data_key(self, key: str, value: Any, state: FSMContext):
        data = await state.get_data()
        data[key] = value
        await state.set_data(data)

    async def _empty_state_data(self, state: FSMContext):
        await state.set_data({
            "recreation": True
        })

            
    def register_handlers(self):
        self.router.message.register(self.go_back, F.text == "Вернуться", StateFilter(States.CARD_MENU))
        self.router.message.register(self.change_media_start, F.text == "Изменить медиа", StateFilter(States.CARD_MENU))
        self.router.message.register(self.change_media_cancel, F.text == "Отмена", StateFilter(States.CHANGE_MEDIA))
        self.router.message.register(self.change_media_handle, F.photo | F.video | F.sticker | F.document, StateFilter(States.CHANGE_MEDIA))
        self.router.message.register(self.recreate_card_name, F.text == "Заполнить анкету заного", StateFilter(States.CARD_MENU))
