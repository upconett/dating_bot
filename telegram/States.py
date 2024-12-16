from telegram import State, StatesGroup


class States(StatesGroup):
    START = State()

    REQUEST_NAME = State()
    REQUEST_AGE = State()
    REQUEST_CITY = State()
    REQUEST_SEX = State()
    REQUEST_MEDIA = State()
    REQUEST_INTERESTS = State()
    REQUEST_DESCRIPTION = State()

    CARD_APPROVE = State()

    REQUEST_WHO_SEEK = State()
    REQUEST_AGE_SEEK = State()

    TO_RECOMENDATIONS = State()

    RECOMENDATIONS = State()

    IDLE = State()
    CARD_MENU = State()

    CHANGE_MEDIA = State()

    MESSAGE_CARD = State()
