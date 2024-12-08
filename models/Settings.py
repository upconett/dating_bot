from typing import Optional

from dataclasses import dataclass

from models import Sex


@dataclass
class Settings:
    seek_age_from: int
    seek_age_to: int
    seek_sex: Sex
