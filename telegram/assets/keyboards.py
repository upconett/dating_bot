from typing import List, Optional, Any

from telegram import InlineKeyboard, ReplyKeyboard, ReplyKeyboardRemove
from telegram import InlineButton, ReplyButton
from telegram import InlineKeyboardBuilder, ReplyKeyboardBuilder

from models import Interest, Card, Payment, User


empty = ReplyKeyboardRemove()


def _create_one_interest_button(interest: Interest, chosen: bool) -> InlineButton:
    return InlineButton(
        text=("✅ " if chosen else "") + interest.russian_name,
        callback_data=f"choose_interest_{interest.value}"
    ) 


def _create_interest_buttons(chosen_interests: List[int]) -> List[InlineButton]:
    buttons = [
        _create_one_interest_button(interest, chosen=True)
        if interest.value in chosen_interests
        else
        _create_one_interest_button(interest, chosen=False)

        for interest in Interest # <- that's enum
    ]
    return buttons


start_card_creation = ReplyKeyboard(
    keyboard=[[ReplyButton(text="Создать анкету")]],
    resize_keyboard=True,
    one_time_keyboard=True
)


choose_sex = ReplyKeyboard(
    keyboard=[
        [
            ReplyButton(text="Парень"),
            ReplyButton(text="Девушка")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


choose_no_photo = ReplyKeyboard(
    keyboard=[[ReplyButton(text="Без фото")]],
    resize_keyboard=True,
    one_time_keyboard=True
)


def choose_interests(chosen_interests: List[int] = []) -> InlineKeyboard:
    keyboard = InlineKeyboardBuilder()
    for button in _create_interest_buttons(chosen_interests):
        keyboard.add(button)
    keyboard.add(InlineButton(text="Готово", callback_data="interest_done"))
    keyboard.adjust(3, 3, 3, 3, 1)
    return keyboard.as_markup()


description_empty: InlineKeyboard = (
    InlineKeyboardBuilder()
    .add(InlineButton(text="Оставить пустым", callback_data="description_empty"))
).as_markup()


card_creation_done = ReplyKeyboard(
    keyboard=[
        [
            ReplyButton(text="Да, все ок", callback_data="creation_ok"),
            ReplyButton(text="Заполнить анкету заново", callback_data="creation_restart")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


request_who_seek = ReplyKeyboard(
    keyboard=[
        [ReplyButton(text="Девушек"), ReplyButton(text="Парней")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


recomended_card = ReplyKeyboard(
    keyboard=[
        [
            ReplyButton(text="❤️"),
            ReplyButton(text="💬"),
            ReplyButton(text="💔"),
            ReplyButton(text="💤")
        ]
    ],
    resize_keyboard=True
)


def idle_menu(card: Card) -> ReplyKeyboard:
    toggle_card_text = (
        "Отключить анкету" if card.active
        else "Включить анкету"
    )
    return ReplyKeyboard(
        keyboard=[
            [ReplyButton(text="Смотреть анкеты")],
            [ReplyButton(text="Моя анкета")],
            [ReplyButton(text=toggle_card_text)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


are_you_sure = ReplyKeyboard(
    keyboard = [
        [
            ReplyButton(text="Да"),
            ReplyButton(text="Нет")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


card_menu = ReplyKeyboard(
    keyboard=[
        [ReplyButton(text="Вернуться")],
        [ReplyButton(text="Заполнить анкету заново")],
        [ReplyButton(text="Изменить медиа")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


def response_card(sender: User) -> InlineKeyboard:
    return InlineKeyboard(
        inline_keyboard=[
            [
                InlineButton(text="❤️", callback_data=f"response_like_{sender.tg_id}"),
                InlineButton(text="Жалоба ⚠️", callback_data=f"report_{sender.id}"),
                InlineButton(text="💔", callback_data=f"response_dislike_{sender.tg_id}"),
            ],
        ],
    )


message_cancel: InlineKeyboard = (
    InlineKeyboardBuilder()
    .add(InlineButton(text="Отмена", callback_data="message_cancel"))
)


continue_recomendation = ReplyKeyboard(
    keyboard=[[ReplyButton(text="Смотреть анкеты")]],
    resize_keyboard=True
)

to_recomendations = ReplyKeyboard(
    keyboard=[[ReplyButton(text="Начать общаться!")]],
    resize_keyboard=True
)

CHANGE_MEDIA = ReplyKeyboard(
    keyboard=[[ReplyButton(text="Отмена")]],
    resize_keyboard=True
)

ADMIN_STATS = InlineKeyboard(
    inline_keyboard=[
        [InlineButton(text="Рассылка пока не работает", callback_data="_")],
        [InlineButton(text="График возраста не работает", callback_data="_")]
    ]
)

LIKE_PAYMENT = InlineKeyboard(
    inline_keyboard=[
        [InlineButton(text="Оплатить", callback_data="payment_like")],
        [InlineButton(text="Отмена", callback_data="cancel")]
    ]
)

MESSAGE_PAYMENT = InlineKeyboard(
    inline_keyboard=[
        [InlineButton(text="Оплатить", callback_data="payment_message")],
        [InlineButton(text="Отмена", callback_data="cancel")]
    ]
)

def like_payment_with_url(payment: Payment) -> InlineKeyboard:
    return InlineKeyboard(
        inline_keyboard=[
            [InlineButton(text="Перейти", url=payment.base_url)],
            [InlineButton(text="Проверить оплату", callback_data=f"check_payment_like_{payment.label}")],
            [InlineButton(text="Отмена", callback_data="cancel")]
        ]
    )

def message_payment_with_url(payment: Payment) -> InlineKeyboard:
    return InlineKeyboard(
        inline_keyboard=[
            [InlineButton(text="Перейти", url=payment.base_url)],
            [InlineButton(text="Проверить оплату", callback_data=f"check_payment_message_{payment.label}")],
            [InlineButton(text="Отмена", callback_data="cancel")]
        ]
    )

def report_log(reported_card: Card) -> InlineKeyboard:
    card = reported_card
    return InlineKeyboard(
        inline_keyboard=[
            [
                InlineButton(text="Забанить ⛔", callback_data=f"ban_{card.user_id}"),
                InlineButton(text="Помиловать 😇", callback_data=f"spare")
            ]
        ]
    )
