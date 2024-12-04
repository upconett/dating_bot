from typing import List

from telegram import InlineKeyboard
from telegram import AIOgramMessage, AIOgramQuery, filters, F, StateFilter
from telegram import UpdateHandler, UpdateHandlerConfig

from telegram import FSMContext, States

from telegram.assets import messages, keyboards
from telegram import NotificationManager

from services import UserService

from models import Card



class CardCreationHandler(UpdateHandler):
    notification_manager: NotificationManager
    user_service: UserService


    def __init__(
            self,
            config: UpdateHandlerConfig,
            notification_manager: NotificationManager,
            user_service: UserService
        ):
        super().__init__(config)
        self.notification_manager = notification_manager
        self.user_service = user_service


    async def request_name(self, message: AIOgramMessage, state: FSMContext):
        await message.answer(messages.REQUEST_NAME)
        await state.set_state(States.REQUEST_NAME)


    async def request_age(self, message: AIOgramMessage, state: FSMContext):
        await message.answer(messages.REQUEST_AGE)
        await state.set_state(States.REQUEST_AGE)


    async def request_city(self, message: AIOgramMessage, state: FSMContext):
        await message.answer(messages.REQUEST_CITY)
        await state.set_state(States.REQUEST_CITY)

    
    async def request_sex(self, message: AIOgramMessage, state: FSMContext):
        await message.answer(
            text=messages.REQUEST_SEX,
            reply_markup=keyboards.choose_sex,
        )
        await state.set_state(States.REQUEST_SEX)


    async def request_media(self, message: AIOgramMessage, state: FSMContext):
        await message.answer(
            text=messages.REQUEST_MEDIA,
            reply_markup=keyboards.choose_no_photo
        )
        await state.set_state(States.REQUEST_MEDIA)

    
    async def request_interests(self, message: AIOgramMessage, state: FSMContext):
        await message.answer(
            text=messages.CHOOSE_INTERESTS,
            reply_markup=keyboards.choose_interests()
        )
        await state.set_state(States.REQUEST_INTERESTS)

    
    async def choose_interest(self, query: AIOgramQuery, state: FSMContext):
        data = await state.get_data()
        data = self._update_interests(data, query)
        await query.message.edit_reply_markup(
            reply_markup=keyboards.choose_interests(data.get("interests"))
        )
        await state.set_data(data)
        await query.answer()

    
    async def finish_choosing_interest(self, query: AIOgramQuery, state: FSMContext):
        data = await state.get_data()
        await self._remove_finish_button(query)
        await self._show_created_card(data, query)
        await query.message.answer(
            text=messages.CARD_DONE,
            keyboards=keyboards.card_creation_done
        )


    async def _show_created_card(self, data: dict, query: AIOgramQuery):
        card = self._create_mock_card()
        await query.message.answer(
            text=messages.card_info(card)
        )


    def _create_mock_card(self) -> Card:
        return Card(
            id=-1,
            name="Витя",
            age=20,
            city="Омск",
            interests="00110101",
            description="Я админ тг канала бла бла",
            media=[]
        )

    async def _remove_finish_button(self, query: AIOgramQuery):
        previous_keyboard: InlineKeyboard = query.message.reply_markup
        previous_keyboard.inline_keyboard = previous_keyboard.inline_keyboard[:-1]
        no_finish_button_keyboard = previous_keyboard
        await query.message.edit_reply_markup(
            reply_markup=no_finish_button_keyboard
        )
    
    def _update_interests(self, data: dict, query: AIOgramQuery) -> dict:
        interests = self._get_interests(data)
        chosen_interest = self._extract_interest(query.data)
        self._toggle_interest(interests, chosen_interest)
        return data


    def _extract_interest(self, query_data: str) -> int:
        return int(query_data.split("_")[2])

    
    def _get_interests(self, data: dict) -> List[int]:
        interests: List[int] = data.get("interests")
        if interests is None: data["interests"] = []
        return data["interests"]
        

    def _toggle_interest(self, interests: List[int], chosen: int):
        if chosen in interests:
            interests.remove(chosen)
        else:
            interests.append(chosen)


    def register_handlers(self):
        self.router.message.register(self.request_name, F.text, StateFilter(States.START))
        self.router.message.register(self.request_age, F.text, StateFilter(States.REQUEST_NAME))
        self.router.message.register(self.request_city, F.text, StateFilter(States.REQUEST_AGE))
        self.router.message.register(self.request_sex, F.text, StateFilter(States.REQUEST_CITY))
        self.router.message.register(self.request_media, F.text, StateFilter(States.REQUEST_SEX))
        self.router.message.register(self.request_interests, F.photo | F.video | F.text, StateFilter(States.REQUEST_MEDIA))
        self.router.callback_query.register(self.choose_interest, F.data.startswith("choose_interest_"), StateFilter(States.REQUEST_INTERESTS))
        self.router.callback_query.register(self.finish_choosing_interest, F.data.startswith("interest_done"), StateFilter(States.REQUEST_INTERESTS))