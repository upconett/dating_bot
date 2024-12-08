from dataclasses import dataclass

from typing import Optional, List

from models import Sex


@dataclass
class Card:
    id: int
    user_id: int
    name: str
    sex: Sex
    age: int
    city: str
    interests: str
    description: Optional[str]
    media: Optional[List[str]]
