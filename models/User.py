from typing import Optional

from dataclasses import dataclass

from models import Settings


@dataclass
class User:
    id: int
    tg_id: int
    first_name: str
    last_name: Optional[str]
    username: Optional[str]
    settings: Optional[Settings]

    likes_left: int
    bonus_likes: int

    messages_left: int
    bonus_messages: int

    def __repr__(self):
        return f"User (id:{self.id}, tg_id:{self.tg_id}, {self.first_name}, {self.username or 'no-username'})"