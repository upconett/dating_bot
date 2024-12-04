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