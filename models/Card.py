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
    interests: int               # used in binary format (3 = 00011) means that 1st and 2nd interests are chosen
    description: Optional[str]
    media: List[Media]
