from typing import List
from models import Card, Interest


def _build_interests(interests_string: str) -> List[str]:
    result = []
    for i in range(len(interests_string)):
        if interests_string[i] == '1':
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
    interests_line = "{interests}".format(interests=" ".join(interests))

    if card.description:
        return (
            f"{first_line}\n"
            "\n"
            f"{description_line}\n"
            "\n"
            f"{interests_line}"
        )
    else:
        return (
            f"{first_line}\n"
            "\n"
            f"{interests_line}"
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

INVALID_MEDIA = (
    "Вы можете прикреплять только ФОТО или ВИДЕО"
)

TOO_MANY_MEDIA = (
    "Вы можете прикреплять не более 3х вложений"
)