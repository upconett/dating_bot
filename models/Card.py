from dataclasses import dataclass

from typing import Optional, List

from models import Sex, Media


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
    media: List[Media]
