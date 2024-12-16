import asyncio
from typing import List

from telegram import InlineKeyboard
from telegram import AIOgramMessage, AIOgramQuery, filters, F, StateFilter
from telegram import UpdateHandler, UpdateHandlerConfig
from telegram import ContentType as CT
from telegram import InputMediaPhoto, InputMediaVideo

from telegram import FSMContext, States

from telegram.assets import messages, keyboards
from telegram import ReplyKeyboard, InlineKeyboard
from telegram import NotificationManager

from services import UserService, CardService

from models import Card, Media, User

from telegram.utils.card_creation import *
from telegram.utils.exceptions import *


class CardCreationHandler(UpdateHandler):
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

    
    #region Handles


    async def step_to_name(self, message: AIOgramMessage, state: FSMContext):
        await self._empty_state_data(state)
        await message.answer(messages.REQUEST_NAME, reply_markup=keyboards.empty)
        await state.set_state(States.REQUEST_NAME)


    async def step_name_to_age(self, message: AIOgramMessage, state: FSMContext):
        try: 
            await self._save_name(message.text, state)
            await message.answer(messages.REQUEST_AGE)
            await state.set_state(States.REQUEST_AGE)
        except InvalidName:
            await message.answer(messages.INVALID_NAME)


    async def step_age_to_city(self, message: AIOgramMessage, state: FSMContext):
        try:
            await self._save_age(message.text, state)
            await message.answer(messages.REQUEST_CITY)
            await state.set_state(States.REQUEST_CITY)
        except InvalidAge:
            await message.answer(messages.INVALID_AGE)
        except TooYoung:
            await message.answer(messages.TOO_YOUNG)

    
    async def step_city_to_sex(self, message: AIOgramMessage, state: FSMContext):
        try:
            await self._save_city(message.text, state)
            await message.answer(
                text=messages.REQUEST_SEX,
                reply_markup=keyboards.choose_sex,
            )
            await state.set_state(States.REQUEST_SEX)
        except InvalidCity:
            await message.answer(messages.INVALID_CITY)


    async def step_sex_to_media(self, message: AIOgramMessage, state: FSMContext):
        try:
            await self._save_sex(message.text, state)
            await message.answer(
                text=messages.REQUEST_MEDIA,
                reply_markup=keyboards.empty
            )
            await state.set_state(States.REQUEST_MEDIA)
        except InvalidSex:
            await message.answer(messages.INVALID_SEX)

    
    async def step_media_to_interests(self, message: AIOgramMessage, state: FSMContext, media_group: List[AIOgramMessage]):
        try:
            await self._save_media(message, media_group, state)
            await message.answer(
                text=messages.CHOOSE_INTERESTS,
                reply_markup=keyboards.choose_interests()
            )
            await state.set_state(States.REQUEST_INTERESTS)
        except InvalidMedia:
            await message.answer(messages.INVALID_MEDIA)
        except TooManyMedia:
            await message.answer(messages.TOO_MANY_MEDIA)

    
    async def choose_interest(self, query: AIOgramQuery, state: FSMContext):
        try:
            interests = await self._save_interests(query.data, state)
            await query.message.edit_reply_markup(
                reply_markup=keyboards.choose_interests(interests)
            )
        except Exception as e: print(e) # <- Surpassing "same reply markup" error
        await query.answer()

    
    async def step_interest_to_description(self, query: AIOgramQuery, state: FSMContext):
        await self._remove_finish_button(query.message)
        await self._show_created_card(query.message, state)
        message_to_memorise = await query.message.answer(
            text=messages.REQUEST_DESCRIPTION,
            reply_markup=keyboards.description_empty
        )
        await self._memorise_message(message_to_memorise, state)
        await state.set_state(States.REQUEST_DESCRIPTION)

    
    async def step_description_to_approve(self, message: AIOgramMessage, state: FSMContext):
        await self._save_description(message.text, is_empty=False, state=state)
        memorised_message = await self._get_memorised_message(state)
        if memorised_message:
            await self._remove_finish_button(memorised_message)
        await self._show_created_card(message, state)
        await message.answer(
            text=messages.CARD_DONE,
            reply_markup=keyboards.card_creation_done
        )
        await state.set_state(States.CARD_APPROVE)

    
    async def step_empty_description_to_approve(self, query: AIOgramQuery, state: FSMContext):
        await self._save_description("", is_empty=True, state=state)
        await self._remove_finish_button(query.message)
        await self._show_created_card(query.message, state)
        await query.message.answer(
            text=messages.CARD_DONE,
            reply_markup=keyboards.card_creation_done
        )
        await state.set_state(States.CARD_APPROVE)

    
    async def step_approve_to_recreate(self, message: AIOgramMessage, state: FSMContext):
        await self._empty_state_data(state)
        await message.answer(messages.REQUEST_NAME)
        await state.set_state(States.REQUEST_NAME)


    async def step_card_approve_to_recomendation_settings(self, message: AIOgramMessage, state: FSMContext, user: User):
        card = await self._create_card(state, user)
        await message.answer(
            text=messages.REQUEST_WHO_SEEK,
            reply_markup=keyboards.request_who_seek
        )
        await state.set_state(States.REQUEST_WHO_SEEK)

    
    async def click_on_done_interests(self, query: AIOgramQuery, state: FSMContext):
        await query.answer(messages.CLICK_DONE_INTERESTS)


    #region UtilityMethods


    async def _is_recreation(self, state: FSMContext) -> bool:
        data = await state.get_data()
        recreation = data.get("recreation")
        if recreation: recreation = True
        else: recreation = False
        return recreation

    async def _create_card(self, state: FSMContext, user: User) -> Card:
        state_data = await state.get_data()
        raw_card = self._card_from_state_data(state_data, user)
        if await self._is_recreation(state):
            old_card = await self.card_service.get_by_user(user)
            raw_card.id = old_card.id
            raw_card.user_id = old_card.user_id
            new_card = await self.card_service.update_card(raw_card)
            return new_card
        else:
            card = await self.card_service.create(raw_card, user)
            return card


    async def _show_created_card(self, message: AIOgramMessage, state: FSMContext):
        data = await state.get_data() # TODO : use later
        card = Card(
            id=1,
            user_id=message.from_user.id,
            name=data.get("name"),
            sex=Sex(data.get("sex")),
            age=data.get("age"),
            city=data.get("city"),
            interests=self._interests_to_int(data.get("interests")),
            description=data.get("description"),
            media=data.get("media")
        )
        await self._send_message_with_media(
            message,
            media=card.media,
            text=messages.card_info(card),
        )

    
    def _interests_to_int(self, interests: List[int]) -> str: # TODO : REMOVE, should be inside CardService
        arr = [0] * len(Interest)
        for interest in interests:
            arr[interest] = 1
        result = ""
        for a in arr: result = str(a) + result
        return int(result, 2)


    async def _remove_finish_button(self, message: AIOgramMessage):
        await message.edit_reply_markup(
            reply_markup=previous_keyboard_without_last_button(message)
        )


    async def _save_name(self, text: str, state: FSMContext):
        if not valid_name(text): raise InvalidName()
        await self._add_state_data_key("name", text, state)

    
    async def _save_age(self, text: str, state: FSMContext):
        if not valid_age(text): raise InvalidAge()
        age = extract_age(text)
        if too_young(age): raise TooYoung()
        await self._add_state_data_key("age", age, state)

    
    async def _save_city(self, text: str, state: FSMContext):
        if not valid_city(text): raise InvalidCity()
        await self._add_state_data_key("city", text, state)

    
    async def _save_sex(self, text: str, state: FSMContext):
        if not valid_sex(text): raise InvalidSex()
        sex = extract_sex(text)
        await self._add_state_data_key("sex", sex.value, state)

    
    async def _save_interests(self, callback_data: str, state: FSMContext) -> List[Interest]:
        data = await state.get_data()
        interests = update_interests(data, callback_data)
        await state.set_data(data)
        return interests

    
    async def _save_description(self, text: str, is_empty: bool, state: FSMContext):
        if is_empty:
            await self._add_state_data_key("description", None, state)
        else:
            if not valid_description(text): raise InvalidDescription()
            await self._add_state_data_key("description", text, state)

        
    async def _empty_state_data(self, state: FSMContext):
        data = await state.get_data()
        recreation = data.get("recreation")
        if recreation: recreation = True
        else: recreation = False
        await state.set_data({
            "recreation": recreation
        })

    
    async def _memorise_message(self, message: AIOgramMessage, state: FSMContext):
        await self._add_state_data_key("memorised_message", message, state)
    

    async def _get_memorised_message(self, state: FSMContext) -> AIOgramMessage:
        data = await state.get_data()
        return data.get("memorised_message")

    
    async def _save_media(self, message: AIOgramMessage, media_group: List[AIOgramMessage], state: FSMContext):
        if media_group is not None:
            media = self._collect_media(media_group)
            await self._add_state_data_key("media", media, state)
        elif message.content_type in (CT.PHOTO, CT.VIDEO):
            media = self._get_photo_or_video(message)
            await self._add_state_data_key("media", media, state)
        elif message.content_type == CT.TEXT:
            await self._add_state_data_key("media", [], state)
        else:
            raise InvalidMedia


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
            
        
    def _media_present(self, message: AIOgramMessage, media_group: List[AIOgramMessage]) -> bool:
        return (media_group or (message.content_type in (CT.PHOTO, CT.VIDEO)))

    
    def _get_photo_or_video(self, message: AIOgramMessage) -> List[Media]:
        if message.photo:
            return [Media("photo", message.photo[-1].file_id)]
        elif message.video:
            return [Media("video", message.video.file_id)]
        else:
            raise InvalidMedia()


    async def _add_state_data_key(self, key: str, value: Any, state: FSMContext):
        data = await state.get_data()
        data[key] = value
        await state.set_data(data)


    def _card_from_state_data(self, state_data: dict, user: User) -> Card:
        return Card(
            id=user.id,
            user_id=user.tg_id,
            name=state_data.get("name"),
            sex=Sex(state_data.get("sex")),
            age=state_data.get("age"),
            city=state_data.get("city"),
            interests=self._interests_to_int(state_data.get("interests")),
            description=state_data.get("description"),
            media=state_data.get("media")
        )

    
    async def _send_message_with_media(self, message: AIOgramMessage, media: List[Media], text: str = None, keyboard: InlineKeyboard | ReplyKeyboard = None) -> AIOgramMessage:
        if len(media) == 1:
            return await self._send_single_media(message, media[0], text, keyboard)
        elif len(media) > 1:
            return await self._send_media_group(message, media, text)
        else:
            return await message.answer(text=text, reply_markup=keyboard)

        
    async def _send_media_group(self, message: AIOgramMessage, media: List[Media], text: str) -> AIOgramMessage:
        media_group: List[InputMediaPhoto|InputMediaVideo] = []
        for m in media:
            if m.type == "photo": media_group.append(InputMediaPhoto(media=m.file_id))
            if m.type == "video": media_group.append(InputMediaVideo(media=m.file_id))
        media_group[0].caption = text
        return await message.answer_media_group(media_group)


    async def _send_single_media(self, message: AIOgramMessage, media: Media, text: str, keyboard: InlineKeyboard | ReplyKeyboard) -> AIOgramMessage:
        match(media.type):
            case "photo":
                await message.answer_photo(
                    photo=media.file_id,
                    caption=text,
                    reply_markup=keyboard
                )
            case "video":
                await message.answer_video(
                    video=media.file_id,
                    caption=text,
                    reply_markup=keyboard
                )


    #region register


    def register_handlers(self):
        self.router.message.register(self.step_to_name, F.text, StateFilter(States.START))
        self.router.message.register(self.step_name_to_age, F.text, StateFilter(States.REQUEST_NAME))
        self.router.message.register(self.step_age_to_city, F.text, StateFilter(States.REQUEST_AGE))
        self.router.message.register(self.step_city_to_sex, F.text, StateFilter(States.REQUEST_CITY))
        self.router.message.register(self.step_sex_to_media, F.text, StateFilter(States.REQUEST_SEX))
        self.router.message.register(self.step_media_to_interests, F.photo | F.video | F.sticker | F.document,  StateFilter(States.REQUEST_MEDIA))
        self.router.callback_query.register(self.choose_interest, F.data.startswith("choose_interest_"), StateFilter(States.REQUEST_INTERESTS))
        self.router.callback_query.register(self.step_interest_to_description, F.data.startswith("interest_done"), StateFilter(States.REQUEST_INTERESTS))
        self.router.message.register(self.step_description_to_approve, F.text, StateFilter(States.REQUEST_DESCRIPTION))
        self.router.callback_query.register(self.step_empty_description_to_approve, F.data == "description_empty", StateFilter(States.REQUEST_DESCRIPTION))
        self.router.message.register(self.step_approve_to_recreate, F.text == "Заполнить анкету заново", StateFilter(States.CARD_APPROVE))
        self.router.callback_query.register(self.click_on_done_interests, F.data.startswith("choose_interest_"))
        self.router.message.register(self.step_card_approve_to_recomendation_settings, F.text == "Да, все ок", StateFilter(States.CARD_APPROVE))
