from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Card:
    id: int
    name: str
    age: int
    city: str
    interests: str
    description: Optional[str]
    media: Optional[List[str]]

