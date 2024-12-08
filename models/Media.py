from typing import Literal
from dataclasses import dataclass


@dataclass
class Media:
    type: Literal["photo", "video"]
    file_id: str
