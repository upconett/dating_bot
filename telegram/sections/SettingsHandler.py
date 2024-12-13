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

from models import User, Settings

from telegram.utils.card_creation import *
from telegram.utils.exceptions import *


class SettingsHandler(UpdateHandler):
    user_service: UserService


    def __init__(
            self,
            config: UpdateHandlerConfig,
            user_service: UserService,
        ):
        super().__init__(config)
        self.user_service = user_service

    
    #region Handles
    

    async def step_seek_sex_to_seek_age(self, message: AIOgramMessage, state: FSMContext):
        try:
            await self._save_sex(message.text, state)
            await message.answer(
                text=messages.REQUEST_AGE_SEEK,
                reply_markup=keyboards.empty
            )
            await state.set_state(States.REQUEST_AGE_SEEK)
        except InvalidSex:
            await message.answer(messages.INVALID_SEEK_SEX)

        
    async def step_seek_age_to_recomendations(self, message: AIOgramMessage, state: FSMContext, user: User):
        try:
            await self._save_seek_age(message.text, state)
            user.settings = await self._settings_from_state_data(state)
            await self.user_service.update_user(user)
            await message.answer(
                text=messages.SETTINGS_DONE,
                reply_markup=keyboards.to_recomendations
            )
            await state.set_state(States.TO_RECOMENDATIONS)
        except InvalidAge:
            await message.answer(messages.INVALID_SEEK_AGE_FORMAT)
        except TooYoung:
            await message.answer(messages.INVALID_SEEK_AGE)

    
    #region UtilityMethods


    async def _save_sex(self, text: str, state: FSMContext):
        if not valid_sex(text): raise InvalidSex()
        sex = extract_sex(text)
        await self._add_state_data_key("seek_sex", sex, state)


    async def _save_seek_age(self, text: str, state: FSMContext):
        if not self._valid_age_boundaries(text): raise InvalidAge()
        age_from, age_to = self._extract_age_boundaries(text)
        if age_from > age_to: raise InvalidAge()
        if age_from < 16: raise TooYoung()
        if age_to < 16: raise TooYoung()
        await self._add_state_data_key("seek_age_from", age_from, state)
        await self._add_state_data_key("seek_age_to", age_to, state)


    async def _add_state_data_key(self, key: str, value: Any, state: FSMContext):
        data = await state.get_data()
        data[key] = value
        await state.set_data(data)


    def _valid_age_boundaries(self, str_age: str) -> bool:
        if len(str_age) != 5:
            return False
        if str_age[2] != '-':
            return False
        try:
            int(str_age[:2])
            int(str_age[3:])
        except:
            return False
        return True

    def _extract_age_boundaries(self, str_age: str) -> tuple[int, int]:
        seek_age_from = int(str_age[:2])
        seek_age_to = int(str_age[3:])
        return (seek_age_from, seek_age_to)

    
    async def _settings_from_state_data(self, state: FSMContext) -> Settings:
        data = await state.get_data()
        return Settings(
            seek_age_from=data.get("seek_age_from"),
            seek_age_to=data.get("seek_age_to"),
            seek_sex=data.get("seek_sex")
        )


    #region register


    def register_handlers(self):
        self.router.message.register(self.step_seek_sex_to_seek_age, F.text, StateFilter(States.REQUEST_WHO_SEEK))
        self.router.message.register(self.step_seek_age_to_recomendations, F.text, StateFilter(States.REQUEST_AGE_SEEK))
       


