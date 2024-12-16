from typing import List
from models import Card, Interest, Sex, User


def _build_interests(interests: int) -> List[str]:
    result = []
    bin_interests = (bin(interests)[2:])[::-1]
    for i in range(len(bin_interests)):
        if bin_interests[i] == '1':
            result.append(Interest.from_value(i).russian_name)
    return result


START = (
    "Привет, я помогу найти друга или "
    "вторую половинку."
)

REQUEST_NAME = (
    "Давай начнем! Как тебя зовут?"
)

REQUEST_AGE = (
    "Сколько тебе лет?"
)

REQUEST_CITY = (
    "Из какого ты города?"
)

REQUEST_SEX = (
    "Какого ты пола?"
)

REQUEST_MEDIA = (
    "Пришли свое фото"
)

CHOOSE_INTERESTS = (
    "Супер! Осталось совсем не много."
    "Выбери свои интересы, чтобы было легче "
    "найти пару."
)

    
def card_info(card: Card) -> str:
    first_line = "{name}, {city}, {age}".format(**card.__dict__)
    description_line = "{description}".format(**card.__dict__)

    interests = _build_interests(card.interests)
    interests_line = ""
    for i in range(len(interests)):
        interests_line += f"{interests[i]} "
        if (i+1) % 2 == 0:
            interests_line += "\n"

    if card.description:
        return (
            f"{first_line}\n"
            "\n"
            f"{description_line}\n"
            "\n"
            f"<b>{interests_line}</b>"
        )
    else:
        return (
            f"{first_line}\n"
            "\n"
            f"<b>{interests_line}</b>"
        )



REQUEST_DESCRIPTION = (
    "И последнее: Напиши немного о себе "
    "(до 100 символов) или оставь это поле пустым"
)

CARD_DONE = (
    "Отлично, твоя анкета готова, "
    "если все ок, перейдем к поиску пары."
)

REQUEST_WHO_SEEK = (
    "Кого ты ищешь?"
)

REQUEST_AGE_SEEK = (
    "Какого возраста ты ищешь?\n"
    "Введи в формате 17-21."
)

SETTINGS_DONE = (
    "Супер. Можешь переходить к анкетам."
)


# for tests
if __name__ == '__main__':
    card = Card(
        id=1,
        name="Витя",
        age=20,
        city="Омск",
        interests="11111000",
        description="Я админ тг канала бла бла",
        media=[]
    )
    print(card_info(card))


INVALID_NAME = (
    "Введите имя длиной не более 20 символов!"
)

INVALID_AGE = (
    "Введите только одно число - ваш возраст."
)

TOO_YOUNG = (
    "Вы должны быть старше 16 чтобы пользоваться ботом."
)

INVALID_CITY = (
    "Введите город одним словом, не более 20 символов!"
)

INVALID_SEX = (
    "Введите либо \"Парень\", либо \"Девушка\"."
)

INVALID_SEEK_SEX = (
    "Введите либо \"Девушек\", либо \"Парней\"."
)

INVALID_SEEK_AGE_FORMAT = (
    "Введите возраст в формате <от>-<до>\n"
    "Например: \"17-21\" или \"18-18\""
)

INVALID_SEEK_AGE = (
    "Возраст для поиска должен быть больше 16"
)

INVALID_MEDIA = (
    "Вы можете прикреплять только ФОТО или ВИДЕО"
)

TOO_MANY_MEDIA = (
    "Вы можете прикреплять не более 3х вложений"
)

CLICK_DONE_INTERESTS = (
    "Выбранные вами интересы"
)

IDLE_MENU = (
    "Подождем пока твою анкету кто-то увидит"
)

YOU_BEEN_LIKED = (
    "Кому-то понравилась твоя анкета!"
)

def response_like(user: User, card: Card) -> str:
    match (card.sex):
        case Sex.MALE: answered = "ответил"
        case Sex.FEMALE: answered = "ответила"
        case _: answered = "ответил/а"
    user_link = f'<a href="tg://user?id={user.tg_id}">{user.first_name}</a>'
    user_username = f'(@{user.username})' if user.username else ""
    return (
        f"{user_link} {user_username} {answered} тебе!\n"
        "Приятного общения\n"
        "*если ссылки на пользователя нет, значит его настройки приватности не позволяют её получить :("
    )

def received_message(message: str) -> str:
    return (
        "Кому-то понравилась твоя анкета!\n"
        f"💬 Сообщение: {message}"
    )

def link_to_user(user: User) -> str:
    user_username = f'(@{user.username})' if user.username else ""
    return (
        "\n\nСупер! Вот контакт: "
        f'<a href="tg://user?id={user.tg_id}">{user.first_name}</a> {user_username}'
    )

def message_card(card: Card) -> str:
    return (
        f"Введи сообщение для {card.name}"
    )

MESSAGE_SENT = (
    "Сообщение отправлено!"
)

YOUR_CARD = (
    "Так выглядит твоя анкета"
)

CHANGE_MEDIA = (
    "Пришлите до 3 ФОТО или ВИДЕО"
)
