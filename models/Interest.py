from enum import Enum


class Interest(Enum):
    TRAVEL = (0, "✈️ Путешествия")
    IT = (1, "👩‍💻 IT")
    BOOKS = (2, "📚 Книги")
    FITNESS = (3, "💪 Фитнес")
    FOOTBALL = (4, "⚽️ Футбол")
    PAINT = (5, "🎨 Рисование")
    CARS = (6, "🚗 Автомобили")
    GAMING = (7, "👾 Игры")
    CYCLING = (8, "🚴‍♂️ Велоспорт")


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
