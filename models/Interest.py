from enum import Enum


class Interest(Enum):
    TRAVEL = (0, "✈️Путешествия")
    IT = (1, "👩‍💻IT")
    BOOKS = (2, "📚Книги")
    FITNESS = (3, "💪Спорт")
    GAMING = (4, "🕹Игры")
    CINEMA = (5, "🍿Кино и сериалы")
    ANIME = (6, "⛩Аниме")
    PAINT = (7, "🖼Исскуство")
    MUSIC = (8, "🎧Музыка")
    STILE = (9, "👠Мода")
    COOKING = (10, "🍝Кулинария")
    PETS = (11, "🐶Домашние животные")


    @classmethod
    def from_value(cls, value: int):
        """Retrieve enum member by value."""
        for member in cls:
            if member.value == value:
                return member
        raise ValueError(f"{value} is not a valid {cls.__name__}")


    def __init__(self, value: int, russian_name: str):
        self._value_ = value
        self.russian_name = russian_name
