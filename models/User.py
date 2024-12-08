from typing import Optional

from dataclasses import dataclass

from models import Settings


@dataclass
class User:
    id: int
    first_name: str
    last_name: Optional[str]
    username: Optional[str]
    settings: Optional[Settings]
