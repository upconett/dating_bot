from typing import List, Any

from models import Card, Sex, Interest
from telegram import (
    AIOgramMessage,
    AIOgramQuery,
    InlineKeyboard,
    FSMContext
)

from telegram.utils.exceptions import *


def create_mock_card() -> Card:
    return Card(
        id=-1,
        name="Витя",
        age=20,
        city="Омск",
        interests="00110101",
        description="Я админ тг канала бла бла",
        media=[]
    )


def update_interests(data: dict, callback_data: str) -> List[Interest]:
    interests = _get_interests(data)
    chosen_interest = _extract_interest(callback_data)
    _toggle_interest(interests, chosen_interest)
    return interests


def _extract_interest(query_data: str) -> int:
    return int(query_data.split("_")[2])


def _get_interests(data: dict) -> List[int]:
    interests: List[int] = data.get("interests")
    if interests is None: data["interests"] = []
    return data["interests"]
    

def _toggle_interest(interests: List[int], chosen: int):
    if chosen in interests:
        interests.remove(chosen)
    else:
        interests.append(chosen)


def previous_keyboard_without_last_button(message: AIOgramMessage) -> InlineKeyboard:
    previous_keyboard: InlineKeyboard = message.reply_markup
    
    previous_keyboard.inline_keyboard = previous_keyboard.inline_keyboard[:-1]
    return previous_keyboard


def message_from_event(event: AIOgramMessage | AIOgramQuery) -> AIOgramMessage:
    if event.__class__ == AIOgramMessage:
        return event
    else:
        return event.message


def description_is_empty(event: AIOgramMessage | AIOgramQuery) -> bool:
    if event.__class__ == AIOgramQuery:
        return True
    else:
        return False


def valid_name(name: str) -> bool:
    return len(name) <= 20


def valid_age(age: str) -> bool:
    try:
        int(age.split()[0])
    except:
        return False
    if len(age.split()) > 1:
        return False
    if len(age) > 3:
        return False
    return True


def too_young(age: int) -> bool:
    return age < 16
    

def extract_age(age_str: str) -> int:
   return int(age_str.split()[0])


def valid_city(city_str: str) -> bool:
    if (
        len(city_str.split()) != 1 or
        len(city_str) > 20
    ):
        return False
    return True


def valid_sex(sex_str: str) -> bool:
    return sex_str[:3].lower() in ("пар", "дев")


def extract_sex(sex_str: str) -> Sex:
    match (sex_str[:3].lower()):
        case "пар": return Sex.MALE
        case "дев": return Sex.FEMALE


def valid_description(description_str: str) -> bool:
    return 1 <= len(description_str) <= 100
